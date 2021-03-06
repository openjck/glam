<script>
import { createEventDispatcher } from 'svelte';
import { tweened } from 'svelte/motion';
import { cubicOut as easing } from 'svelte/easing';
import { OptionMenu, Option, OptionDivider } from '@graph-paper/optionmenu';

import ProbeExplorer from './ProbeExplorer.svelte';
import KeySelectionControl from '../controls/KeySelectionControl.svelte';
import TimeHorizonControl from '../controls/TimeHorizonControl.svelte';
import ProportionMetricTypeControl from '../controls/ProportionMetricTypeControl.svelte';
import ProbeKeySelector from '../controls/ProbeKeySelector.svelte';
import ColorSwatch from '../controls/ColorSwatch.svelte';

import { formatPercent, formatCount, formatPercentDecimal } from '../../utils/formatters';
import { overTimeTitle, proportionsOverTimeDescription } from '../../utils/constants';
import { gatherProbeKeys, gatherAggregationTypes } from '../../utils/probe-utils';
import { numericStringsSort } from '../../utils/sort';
import { numHighlightedBuckets } from '../../config/shared';

export let aggregationLevel = 'build_id';
export let data;
export let probeType;
export let activeBuckets;
export let bucketColorMap;
export let bucketOptions;
export let timeHorizon = 'MONTH';
export let metricType = 'proportions';

export let bucketSortOrder = (a, b) => ((a < b) ? 1 : -1);

const dispatch = createEventDispatcher();

function makeSelection(type) {
  return function onSelection(event) {
    dispatch('selection', { selection: event.detail.selection, type });
  };
}

let aggregationTypes = gatherAggregationTypes(data);
let probeKeys = gatherProbeKeys(data);
let currentKey = probeKeys[0];
let currentAggregation = aggregationTypes[0];

// set the audience size when the reference updates.
let reference;
const movingAudienceSize = tweened(0, { duration: 500, easing });
$: if (reference) movingAudienceSize.set(reference.audienceSize);

$: if (currentKey && reference) {
  const ref = data[currentKey][currentAggregation].find((d) => (
    d.label.toString() === reference.label.toString()
  ));
  reference = ref;
}

function filterResponseData(d, agg, key) {
  return d.filter((di) => di.client_agg_type === agg && di.metric_key === key);
}

$: selectedData = filterResponseData(data, currentAggregation, currentKey);

let showOptionMenu = false;
let coloredBuckets = [];
let everActiveBuckets = [];
let sortedImportantBuckets = [];
let sortedUnimportantBuckets = [];

if (bucketOptions.length > numHighlightedBuckets) {
  showOptionMenu = true;
  const lastDataset = data[data.length - 1];

  coloredBuckets = Object.entries(lastDataset.counts).sort((
    [bucketAName, bucketAValue],
    [bucketBName, bucketBValue],
  ) => {
    const bucketValueDifference = bucketAValue - bucketBValue;
    if (bucketValueDifference === 0) {
      return bucketBName - bucketAName;
    }
    return bucketValueDifference;
  }).slice(-numHighlightedBuckets).map(([bucket]) => bucket);
}

$: if (showOptionMenu) {
  everActiveBuckets = [...new Set([
    ...activeBuckets,
    ...everActiveBuckets,
  ])];

  // An important bucket is any bucket that:
  //
  //   (a) is colored
  //   (b) is currently active
  //   (c) has been active at some point in the past
  //
  // Rule (c) improves usability: if the user goes out of their way to enable a
  // bucket that we consider to be unimportant, we should consider it to be
  // important for the rest of the interaction. If we did not do this, the bucket
  // would switch between the important group and the unimportant group as it's
  // toggled, which would be annoying.
  sortedImportantBuckets = [...new Set([
    ...everActiveBuckets,
    ...coloredBuckets,
  ])].sort(numericStringsSort);

  // An unimportant bucket is any other bucket
  sortedUnimportantBuckets = bucketOptions.filter((bucket) => (
    !sortedImportantBuckets.includes(bucket)
  )).sort(numericStringsSort);
}
</script>

<style>
.body-content {
  margin-top: var(--space-2x);
}

.data-graphics {
  margin-top: var(--space-4x);
}

.small-multiple {
  margin-bottom: var(--space-8x);
}
</style>


<div class=body-content>

  <slot></slot>

  <div class="body-control-row body-control-row--stretch">
    <div class=body-control-set>
      {#if aggregationLevel === 'build_id'}
      <label class=body-control-set--label>Time Horizon  </label>
      <TimeHorizonControl
        horizon={timeHorizon}
        on:selection={makeSelection('timeHorizon')}
      />
      {/if}
    </div>

    <div class=body-control-set>
      <label class=body-control-set--label>Categories</label>
      {#if showOptionMenu}
        <OptionMenu multi on:selection={(evt) => {
          dispatch('selection', { selection: evt.detail.keys, type: 'activeBuckets' });
        }}>
          {#each sortedImportantBuckets as importantBucket, i (importantBucket)}
            <Option
              selected={activeBuckets.includes(importantBucket)}
              key={importantBucket}
              label={importantBucket}>
              <div class="option-menu__list-item__slot-right" slot="right">
                <ColorSwatch color={bucketColorMap(importantBucket)} />
              </div>
            </Option>
          {/each}
          {#if sortedImportantBuckets.length && sortedUnimportantBuckets.length}
            <OptionDivider />
          {/if}
          {#each sortedUnimportantBuckets as unimportantBucket, i (unimportantBucket)}
            <!--
              By definition, an unimportantBucket is never a selected bucket,
              hence selected={false}
            -->
            <Option
              selected={false}
              key={unimportantBucket}
              label={unimportantBucket}>
              <div slot="right">
                <ColorSwatch color={bucketColorMap(unimportantBucket)} />
              </div>
            </Option>
          {/each}
        </OptionMenu>
      {:else}
        <KeySelectionControl
          sortFunction={bucketSortOrder}
          options={bucketOptions}
          selections={activeBuckets}
          on:selection={makeSelection('activeBuckets')}
          colorMap={bucketColorMap} />
      {/if}
    </div>
  </div>

  <div class="body-control-row  body-control-row--stretch">
    <div class=body-control-set>
      <label class=body-control-set--label>Metric Type</label>
      <ProportionMetricTypeControl
        metricType={metricType}
        on:selection={makeSelection('metricType')}
      />
    </div>
    {#if probeKeys && probeKeys.length > 1}
    <div class=body-control-set>
      <label class=body-control-set--label>Key</label>
        <ProbeKeySelector
          options={probeKeys}
          bind:currentKey={currentKey}
        />
      </div>
    {/if}
  </div>

  <div class=data-graphics>
    {#each probeKeys as key, i (key)}
      {#each aggregationTypes as aggType, i (aggType + timeHorizon + probeType + metricType)}
        {#if key === currentKey && (aggregationTypes.length === 1 || aggType === currentAggregation)}
          <div class='small-multiple'>
            <ProbeExplorer
              bind:reference={reference}
              title={key === 'undefined' ? '' : key}
              aggregationsOverTimeTitle={overTimeTitle(metricType, aggregationLevel)}
              aggregationsOverTimeDescription={proportionsOverTimeDescription(metricType, aggregationLevel)}
              summaryLabel='cat.'
              data={selectedData}
              probeType={probeType}
              activeBins={activeBuckets}
              timeHorizon={timeHorizon}
              binColorMap={bucketColorMap}
              metricType={metricType}
              showViolins={false}
              aggregationLevel={aggregationLevel}
              pointMetricType={metricType}
              yTickFormatter={metricType === 'proportions' ? formatPercent : formatCount}
              summaryNumberFormatter={metricType === 'proportions' ? formatPercentDecimal : formatCount}
              yScaleType={'linear'}
              yDomain={[0, Math.max(...selectedData.map((d) => Object.values(d[metricType])).flat())]}
            >

            </ProbeExplorer>
          </div>
        {/if}
      {/each}
    {/each}
  </div>
</div>
