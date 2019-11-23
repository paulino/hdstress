# hdstress

Another tool to stress disks/devices and find errors.  It is simple tool to run fast test over a HDD, SDD or flash memory. It can be used for:

- Detect HDD/SDD some strange things like inconsistencies not detected by S.M.A.R.T. self tests.
- For flash memories can be detected a capacity fake.

This is tool is a simple tool if you are look for advanced features there are alternatives like:

- *f3 - Fight Flash Fraud* at https://fight-flash-fraud.readthedocs.io
- *StressDisk* at https://github.com/ncw/stressdisk

**hstress** tests a drive in a simple way making two passes:

- Pass 1: writes files into a path using a fixed pattern until the drive mounted in the path is full.
- Pass 2: reads previous files comparing it contents with the expected pattern.

There are a secondary run mode used to stress the drive with concurrent writes and reads. This mode is usefully for HDD drives due it increases the drive temperature and detect more fails. See examples to use this mode.

## Usage

To use hdstress in a easy way to test a device you only must add the path
where it is mounted as parameter:

    hdstress /mnt/test

This command creates 100M Byte files until `/mnt/test` drive is full using an
single job. Then reads files contents and verifying the pattern written previously. It behavior is like a sequential  write and read.

To stress a drive (recommended only for HDD) you can use the following:

    hdstress -j 20 -s 1 /mnt/test

This command creates small files of 1MByte until `/mnt/test` is full. Files are written using 20 threads. Then all files are read to verify the written pattern, the read operation runs 20 threads reading the files in a random order.

On fail, the list of files corrupted are shown and the files are not removed

### Options

The following options are detailed on man page included:

  - **-j N** Number of jobs, concurrent writes and reads. Default 1
  - **-t SIZE** Test size in Gigabytes.
  - **-s SIZE** File size in Megabytes. Default 100, you can reduce this parameter to increase stress for a high number of jobs
  - **-2** verify files previous created files. Used when the program was stopped and the verification pass not ends

## Installation

**hdstress** is written in python and can be used from source code cloning the repository

```bash
git clone https://github.com/paulino/hdstress
cd hdstress
make
cd build
./hdstress -h
```

Also it is installable from the sources at `/usr/local`running a make install:

```bash
git clone https://github.com/paulino/hdstress
cd hdstress
sudo make install
man hdstress
```

Whether your prefer there are  binaries to download for Debian/Ubuntu at release section: https://github.com/paulino/hdstress

## TODO

- Add an option to stop 
- Add an option suppress verbose output

## License

This is free software under the terms of  Apache License Version 2.0 (check the COPYING file included in this package).

## Authors

Paulino Ruiz de Clavijo Vázquez <pruiz@us.es>

