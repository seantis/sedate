Changelog
---------

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
