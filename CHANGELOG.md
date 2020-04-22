# Changelog

## unreleased

- fix bug where store values were reset after authentication ([#429](https://github.com/mozilla/glam/pull/429))
- fix bug with body selectors ([#421](https://github.com/mozilla/glam/pull/421))
- fix bug with aggregation level selector ([#422](https://github.com/mozilla/glam/pull/422))
- move dimension filters into the content body ([#418](https://github.com/mozilla/glam/pull/418))
- automatically adjust process if current one is not valid for probe ([#418](https://github.com/mozilla/glam/pull/418))

## m1

Date: 2020-04-16

- add error handling for 4xx responses
- add specific error handling for 404, when data is not available
- ran prettier on all JS (but not svelte) assets
- clean up unused storybook stories
- fix for keyed enumerated histograms
- add editorconfig to standardize editor code syntax
- add initial support for importing fenix data
- update to API to better support boolean histograms

## m0

Date: 2020-03-26

- Initial tagged release