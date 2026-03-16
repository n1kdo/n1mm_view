#!/bin/bash
#This script will act like n1mm sending contact data over the network.
#You should just need netcat installed
#
#Started by RileyC on 2/20/2024
#

#Define your n1mm collector host and port
def_host=127.0.0.1
def_port=12060
CALLSFILE='cs_files/calls.txt'
SECSFILE='cs_files/sections.txt'
TEMPLATE='cs_files/n1mm_contact_template.xml'

HOST=${2:-$def_host}
PORT=${3:-$def_port}

#This will get a list of all the local xml files and shuffle them, then play them to the collector
for FILE in `cat $CALLSFILE | shuf`

	do
	DDATEE=`date +'%Y-%m-%d %H:%M:%S'`
	random_hex=$(head -c 17 /dev/urandom | xxd -p | tr -d '\n' | cut -c 1-33)
	OPERATORRRR=`grep -v $FILE $CALLSFILE | shuf | tail -1`
	section=`cat $SECSFILE | shuf | tail -1`
	min=10
	max=80
	number=$(expr $min + $RANDOM % $max)	
	gs1=`shuf -n1 -e C D E F`
	gs2=`shuf -n1 -e L M N O`
	mode=`shuf -n1 -e CW USB LSB RTTY PSK31`
	station=`shuf -n1 -e RadioTent1 RadioTent2 RadioTent3 Trailer1 Trailer2`
	frequency=`shuf -n1 -e 352211 1424400 752211 2824400`
	band=`shuf -n1 -e 3.5 7 14 21 28 50 144 420`
	cat $TEMPLATE | sed "s/OPERATORR/$OPERATORRRR/g" | sed "s/REMOTECALLL/$FILE/g" | sed "s/TIMESTAMPPP/$DDATEE/g" | sed "s/IDDDD/$random_hex/g" | sed "s/GRIDDD/${gs1}${gs2}${number}/g" | sed "s/SECTIONNN/$section/g" | sed "s/STATIONNN/$station/g" | sed "s/MODEEE/$mode/g" | sed "s/BANDDD/$band/g" | sed "s/FREQQQ/$frequency/g" | nc -u -w1 $HOST $PORT
	
#	sleep 5
done

