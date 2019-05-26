Unihan JSON
===========

[![Build Status][ci-badge]][ci]

This project generates JSON data files parsed from the [Unicode Han Database]
(Unihan) in a structured way.  Although it's automated through the *process.py*
script, the goal of this project is not the script, but JSON data files.

To download JSON data files, see the [latest release].  To load them from a web
page through XHR or `window.fetch()` function, request the following URI
(replace `<PROP>` with a property name, e.g., `kSimplifiedVariant`):

    https://dahlia.github.io/unihan-json/12.1.0/<PROP>.json

Each JSON file corresponds to a property, and is an object which represents
a table from Unicode characters to values for the property.  For example,
*kCantonese.json* is like:

~~~~~~~~ json
{
	"香": ["hoeng1"],
	"港": ["gong2"],
    ...
}
~~~~~~~~

The following some properties are parsed further into structured values:

    kAccountingNumeric
    kCantonese
    kFrequency
    kGB0
    kGB1
    kGB3
    kGB5
    kGB7
    kGB8
    kGradeLevel
    kHangul
    kHanyuPinlu
    kHanyuPinyin
    kJapaneseKun
    kJapaneseOn
    kLau
    kNelson
    kOtherNumeric
    kPrimaryNumeric
    kSimplifiedVariant
    kTaiwanTelegraph
    kTang
    kTotalStrokes
    kTraditionalVariant
    kVietnamese

The rest properties are merely parsed into string values.  Contributing more
parsers are welcome; see also the `PROP_PARSERS` map in the *process.py* script.

[ci-badge]: https://travis-ci.org/dahlia/unihan-json.svg?branch=master
[ci]: https://travis-ci.org/dahlia/unihan-json
[Unicode Han Database]: https://www.unicode.org/reports/tr38/
[latest release]: https://github.com/dahlia/unihan-json/releases/latest
