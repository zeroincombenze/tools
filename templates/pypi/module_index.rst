.. {{name}} documentation master file, created by
   gen_readme.py on {{now}}
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

=============================================
Welcome to {{name}} {{branch}} documentation!
=============================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

.. $merge_docs

.. $if isfile rtd_description.rst
   rtd_description
.. $else
{{description}}
.. $fi
.. $if isfile rtd_features.rst
   rtd_features
.. $fi
.. $if isfile rtd_installation.rst
   rtd_installation
.. $fi
.. $if isfile rtd_usage.rst
   rtd_usage
.. $fi
.. $if isfile rtd_faq
   rtd_faq
.. $fi
.. $if isfile rtd_macro.rst
   rtd_macro
.. $fi


.. include: readme_footer

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
