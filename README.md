Short script using `pytube` and `moviepy` to automate the clipping of YouTube
videos based on spreadsheets' timestamps (i.e. skip the first 6 hours of work
in making highlights sourced from youtube!)

Input Structure
---
With csv's in the current directory containing the following columns:

- link (required)
  - YouTube link
- timestamp (required)
  - in the format `MM:SS`
- description
  - helpful blurb, part of which can be placed in output clip filename
- replay
  - whether or not to clip a larger length, in order to capture replay footage
    (leave blank for no)
- judgement (required)
  - "rating" of the clip, determining whether or not it is worth clipping
- comment
  - additional blurb (I often use to start pre-planning video structure)

Before running, at the top of `clipper.py`, adjust config constants to your
needs.

For an example of input, the following sheet is an example that would work well
with the script defaults.

`hoyle.csv`
----
| link                         | timestamp | description      | replay | judgement |  comment        |
|------------------------------|-----------|------------------|--------|-----------|-----------------|
| https://youtu.be/0T3LtBvANbg | 3:50      | 6 pickup arm hit |        | clean     |                 |
| https://youtu.be/0T3LtBvANbg | 4:10      | straight fleche  |        | nice      |                 |
| https://youtu.be/0T3LtBvANbg | 18:25     | the Novosjolov   |        | perf      |                 |
| https://youtu.be/0T3LtBvANbg | 21:25     | hand pick to won |        | clean     | sadly bad angle |

Running
----

Using `pipenv` to run:

    $ pipenv install
    $ pipenv run python clipper.py
