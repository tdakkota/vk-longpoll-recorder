# VK LongPoll recorder
## To run
`$ python recorder.py --token=<YOUR_TOKEN>`

or

`$ VK_TOKEN=<YOUR_TOKEN>; python recorder.py`

## Advanced examples

To set API version

`$ python recorder.py --api_version='5.80'`

To set LongPoll version(currently supported only 10)

`$ python recorder.py --version=3`

To set LongPoll mode 

`$ python recorder.py --mode=74 # 2 + 8 + 64`

To set output file

`$ python recorder.py --output=myfile`

To set wait time

`$ python recorder.py --wait=25`

To set initial ts

`$ python recorder.py --ts=<YOUR_TS>`

## Requirments
- [requests](https://github.com/psf/requests)
- [google.Fire](https://github.com/google/python-fire)
