#!/bin/bash
#
# Automatically generated from command:
#
# /u/janin/projects/swordfish/svn/src/srs/srs-go-parallel -template /n/banquet/da/janin/projects/swordfish/svn/src/srs/test_templates/simple -dir exp.test -pvar v1 v1 -pvar outfile out -- v2 val2
#
# Batch 0


srs-go -template /n/banquet/da/janin/projects/swordfish/svn/src/srs/test_templates/simple -loglevel WARNING -dir /n/banquet/da/janin/projects/swordfish/svn/src/srs/test_templates/testsuite.dir/17/exp.test/tasks/task0000000 -config /dev/null -- v2 'val2' v1 'val1.1' outfile '/n/banquet/da/janin/projects/swordfish/svn/src/srs/test_templates/testsuite.dir/17/out1'

if [ "$?" -ne 0 ]; then
  ln -s ../tasks/task0000000 /n/banquet/da/janin/projects/swordfish/svn/src/srs/test_templates/testsuite.dir/17/exp.test/failed_tasks/task0000000
else
  srs-go -template /n/banquet/da/janin/projects/swordfish/svn/src/srs/test_templates/simple -loglevel WARNING -dir /n/banquet/da/janin/projects/swordfish/svn/src/srs/test_templates/testsuite.dir/17/exp.test/tasks/task0000000 -config /dev/null -cleanall -- v2 'val2' v1 'val1.1' outfile '/n/banquet/da/janin/projects/swordfish/svn/src/srs/test_templates/testsuite.dir/17/out1'
fi


srs-go -template /n/banquet/da/janin/projects/swordfish/svn/src/srs/test_templates/simple -loglevel WARNING -dir /n/banquet/da/janin/projects/swordfish/svn/src/srs/test_templates/testsuite.dir/17/exp.test/tasks/task0000001 -config /dev/null -- v2 'val2' v1 'val1.2' outfile '/n/banquet/da/janin/projects/swordfish/svn/src/srs/test_templates/testsuite.dir/17/out2'

if [ "$?" -ne 0 ]; then
  ln -s ../tasks/task0000001 /n/banquet/da/janin/projects/swordfish/svn/src/srs/test_templates/testsuite.dir/17/exp.test/failed_tasks/task0000001
else
  srs-go -template /n/banquet/da/janin/projects/swordfish/svn/src/srs/test_templates/simple -loglevel WARNING -dir /n/banquet/da/janin/projects/swordfish/svn/src/srs/test_templates/testsuite.dir/17/exp.test/tasks/task0000001 -config /dev/null -cleanall -- v2 'val2' v1 'val1.2' outfile '/n/banquet/da/janin/projects/swordfish/svn/src/srs/test_templates/testsuite.dir/17/out2'
fi


srs-go -template /n/banquet/da/janin/projects/swordfish/svn/src/srs/test_templates/simple -loglevel WARNING -dir /n/banquet/da/janin/projects/swordfish/svn/src/srs/test_templates/testsuite.dir/17/exp.test/tasks/task0000002 -config /dev/null -- v2 'val2' v1 'val1.3' outfile '/n/banquet/da/janin/projects/swordfish/svn/src/srs/test_templates/testsuite.dir/17/out3'

if [ "$?" -ne 0 ]; then
  ln -s ../tasks/task0000002 /n/banquet/da/janin/projects/swordfish/svn/src/srs/test_templates/testsuite.dir/17/exp.test/failed_tasks/task0000002
else
  srs-go -template /n/banquet/da/janin/projects/swordfish/svn/src/srs/test_templates/simple -loglevel WARNING -dir /n/banquet/da/janin/projects/swordfish/svn/src/srs/test_templates/testsuite.dir/17/exp.test/tasks/task0000002 -config /dev/null -cleanall -- v2 'val2' v1 'val1.3' outfile '/n/banquet/da/janin/projects/swordfish/svn/src/srs/test_templates/testsuite.dir/17/out3'
fi

