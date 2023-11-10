.. $if branch in '16.0' '17.0'
* python 3.8
* postgresql 12.0+ (warning for 14.0)
.. $fi
.. $if branch in '12.0'
* python 3.7
* postgresql 9.6+ (best 10.0+)
.. $fi
.. $if branch in '11.0'
* python 3.6 or 3.7
* postgresql 9.2+ (best 9.5+)
.. $fi
.. $if branch in '6.1' '7.0' '8.0' '9.0' '10.0'
* python 2.7+ (best 2.7.5+)
* postgresql 9.2+ (best 9.5)
.. $fi
