#!/bin/bash

result=""
while read line
do 
	result=$result$line"\r\n"
done < recommend_shares.txt
echo -e $result | mutt -s "shares day by day" 851849117@qq.com

