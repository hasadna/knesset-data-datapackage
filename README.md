# knesset-data-datapackage
[![travis-ci build status](https://travis-ci.org/hasadna/knesset-data-datapackage.svg)](https://travis-ci.org/hasadna/knesset-data-datapackage)

Provides Knesset data in easy to download and read formats (mostly CSV files).

## Datapackages

Data Packages are a lightweight containerization format for data. They provide the foundation for frictionless data transport. You can read more about the concept and format of [Friction less data](http://frictionlessdata.io) [specs](https://github.com/frictionlessdata/specs) and [datapackage tooling and other related code](https://github.com/frictionlessdata)

## Downloading a prepared datapackage zip

We have a travis job that creates a datapackage for the last 120 days every week and a smaller package for last 5 days every day

Getting the latest zip:

* check the travis build log for "master" branch - https://travis-ci.org/hasadna/knesset-data-datapackage/branches
* pick one of the last successful builds
* scroll to the bottom of the build log
* look for the url, it looks something like this: https://s3.amazonaws.com/knesset-data/datapackage_last_5_days_2017-02-28.zip

Once you downloaded the zip, you can extract and it should be self-explanatory, it contains csv files and other resources.

## Creating a datapackage zip from scratch

If you have more advanced requirements or would like to get a datapackage for a longer time-range you can create the datapackage zip file yourself

**Warning** Knesset APIs are known to be problematic, and sometimes block access for unknown reasons.

Creating a datapackage using the CLI tool:

* Prerequisites
  * you are inside an activated python 2.7 virtualenv
    * `virtualenv knesset-datapackage`
    * `cd knesset-datapackage`
    * `. bin/activate`
* Prepare the environment
  * pip install https://github.com/hasadna/knesset-data-python/archive/master.zip
  * pip install https://github.com/hasadna/knesset-data-datapackage/archive/master.zip
* Run the CLI tool
  * make_knesset_datapackage --help
  * by default the CLI tool creates the output and zip files inside data directory (e.g. knesset-data-datapackage/data)
  * you should delete existing files before creating a new datapackage
