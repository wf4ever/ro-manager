ROPATH="."
ROSRS_URI="http://sandbox.wf4ever-project.org/rodl/ROs/"
ROSRS_ACCESS_TOKEN="32801fc0-1df1-4e34-b"
RO=ro

$RO config -v \
  -b $ROPATH \
  -r $ROSRS_URI \
  -t "$ROSRS_ACCESS_TOKEN" \
  -n "Test user" \
  -e "testuser@example.org"

