LIST:    aws s3api list-objects-v2 --bucket $BUCKET --prefix $PREFIX
GET:     aws s3api get-object --bucket $BUCKET --key $KEY $outfile
HEAD:    aws s3api head-object --bucket $BUCKET --key $KEY
COPY:    aws s3api copy-object --bucket $BUCKET --key $NEWKEY --copy-source $BUCKET/$OLDKEY
