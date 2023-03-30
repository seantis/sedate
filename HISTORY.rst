Changelog
---------

1.0.3 (2023-03-30)
~~~~~~~~~~~~~~~~~~~

- Fixes up packaging of ``py.typed`` marker
  [Daverball]

1.0.2 (2022-08-10)
~~~~~~~~~~~~~~~~~~~

- Adds back removed ``weeknumber`` function
  [Daverball]

1.0.1 (2022-08-09)
~~~~~~~~~~~~~~~~~~~

- Fixes GPLv2 License Classifier in `setup.cfg`
  [Daverball]

1.0.0 (2022-08-09)
~~~~~~~~~~~~~~~~~~~

- Fixes ``align_to_week`` and ``align_to_month`` not behaving consistently with ``align_to_day`` during DST transitions
  [Daverball]

- Fixes DST related issues in ``get_date_range``, ``dtrange`` and ``weekrange``

  With this change these functions now accept additional arguments
  that determine what happens with ambiguous, non-existent times
  during daylight savings transitions.
  [Daverball]

- Adds type annotations
  [Daverball]

- Removes support for Python 2.7 and 3.6 and below
  [Daverball]

- Removes explicit support for Python 3.3 (might or might not work).
  [href]

0.3.0 (2018-02-12)
~~~~~~~~~~~~~~~~~~~

- Adds a weeknumber function.
  [href]

0.2.0 (2017-03-02)
~~~~~~~~~~~~~~~~~~~

- Adds the ability to iterate over custom deltas between a start and an end.
  [href]

- Adds the ability to iterate over weeks between a start and an end.
  [href]

0.1.0 (2016-05-12)
~~~~~~~~~~~~~~~~~~~

- Adds methods to align dates to months and weeks.
  [href]

0.0.5 (2016-04-25)
~~~~~~~~~~~~~~~~~~~

- Adds a time parsing function which accepts anything from 00:00 to 24:00.
  [href]

0.0.4 (2015-11-18)
~~~~~~~~~~~~~~~~~~~

- Fixes an issue with daylight savings time and ``align_date_to_day``.

  With this change, ``align_date_to_day`` ensures that the resulting date is
  in the timezone the date was aligned to, not in the timezone it originally
  was in.
  [href]

0.0.3 (2015-08-05)
~~~~~~~~~~~~~~~~~~~

- Adds a function to turn date-ish objects into datetimes.
  [href]

0.0.2 (2015-08-04)
~~~~~~~~~~~~~~~~~~~

- Fix align_date_to_day failing with certain timezones.
  [href]

0.0.1 (2015-06-30)
~~~~~~~~~~~~~~~~~~~

- Initial Release
