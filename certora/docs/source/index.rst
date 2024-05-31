.. Certora training for ether.fi master file, created by sphinx-quickstart on Fri May 10 15:25:02 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Certora training for ether.fi
=============================

These are lecture notes for the Certora Prover training for ether.fi.

* The repository containing the code for the exercises (and these notes) is
  :clink:`Certora's fork of etherfi's smart-contracts (certora-training branch) </>`.
* We shall use ``certora-cli-beta 7.6.3`` or higher.


.. toctree::
   :maxdepth: 1
   :caption: Contents:
   :numbered: 2

   lesson1/index
   lesson2/index
   lesson3/index
   lesson4/index


.. The following is a trick to get the general index on the side bar.

.. toctree::
   :hidden:

   genindex


Useful links
------------

Lectures recordings
^^^^^^^^^^^^^^^^^^^

#. `First lecture recording`_ (passcode: ``r5xY&4TL``), contents:

   * :doc:`lesson1/index`

#. `First office hours recording`_ (passcode: ``C+*ekg4Q``), contents:

   * Reviewing :doc:`lesson1/exercises`
   * :doc:`lesson1/vacuity`

#. `Second lecture recording`_ (passcode: ``*2lY+64A``), contents:

   * :doc:`lesson2/index`

#. `Recording 24/05`_ (passcode: ``m#35MW@v``), contents:

   * :doc:`lesson2/inv_vs_param`
   * :doc:`lesson2/loops`

#. `Recording 28/05`_ (passcode: ``aU#6LDsH``), contents:

   * Lesson 2 :doc:`lesson3/exercises`

#. `Lecture recording 29/05`_ (passcode: ``w4+dtUT*``), contents:

   * Lesson 4 :doc:`lesson4/index`

#. `Recording 30/05`_ (passcode: ``i.5fK*1W``), discussing examples.

Prover training
^^^^^^^^^^^^^^^
* `Training itinerary`_
* `Prover installation instructions`_
* `Certora Prover documentation`_
* `Certora Prover tutorials`_


Indices and tables
==================

* :ref:`genindex`
* :ref:`search`


.. tip::

   You can create a local version of these pages, with links to your local files.
   First, install the necessary Python dependencies, by running from the root folder of
   this repository *(use a virtual environment!)*: 

   .. code-block:: bash

      pip3 install -r requirements.txt
  
   Next, in :file:`certora/docs/source/conf.py` change the value of ``link_to_github`` to
   ``False``. Finally, run:

   .. code-block:: bash

      sphinx-build -b html certora/docs/source/ certora/docs/build/html

   The html pages will be in :file:`certora/docs/build/html/index.html`.


.. Links:
   ------

.. _Training itinerary:
   https://docs.google.com/document/d/15RDN-3lLDbO3bDOjwtNUHcryOG8udR519yvX4DenZug/edit?usp=sharing
   

.. _Prover installation instructions:
   https://docs.certora.com/en/latest/docs/user-guide/getting-started/install.html

.. _Certora Prover documentation: https://docs.certora.com/
.. _Certora Prover tutorials: Prover installation instructions

.. _First lecture recording:
   https://certora.zoom.us/rec/share/mCUGX9HiOZS3uAUJocUpyDSW-8kRIekaiG01KZEblSQzH2uFac-W5qaFFDKypBmJ.gYaCu1ZCl37iDskQ

.. _First office hours recording:
   https://certora.zoom.us/rec/share/p6w9A6ZzethrJLHfmQ_YW5HzmYDfUEe5O9-QKWaTWzMEiqRM2VRuAoTAkgVqudWT.dYvWaRcUCRjHoR4j

.. _Second lecture recording:
   https://certora.zoom.us/rec/share/U-HnX70alYa3_Tw6c5Y8WpalPVH22qbmrh_J3g00Rzk1jQIfxTj_ifhXiQcUQUci.5HgovB2P0I-0uvil

.. _Recording 24/05:
   https://certora.zoom.us/rec/share/FlHNR2n2Ew-krSkKwcPd5WYcMeQ1l2_PO_79tqFrlI0zD0amLcOmgPiuImKE7UYn.OX6_o4iSVepIoFT_

.. _Recording 28/05:
   https://certora.zoom.us/rec/share/nLib62-k7HNZjvrlULlqntRBfSoQ-l8yFuDg2sDZMmQ3oEVR-3zMJPCZeWaC8B6C.4sf8ZdPduxUyno0x

.. _Lecture recording 29/05:
   https://certora.zoom.us/rec/share/jm669MBOsimi-McB7zQTRvpZBO9bI9A8hsTRDlumCVulDH2C1CKI6p49yo281ity.EWWEHISjfuZHNoha

.. _Recording 30/05:
   https://certora.zoom.us/rec/share/mzBGpXBKl_BopwuPw9_k--AiCOoZfGXAewawu54t9S2JCqjpVWT26UunOIkDHwxw.ISwyc8A3gN5UyOIJ
