Changelog
---------

Unreleased
~~~~~~~~~~

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
