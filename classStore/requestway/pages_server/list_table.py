from flask import request

import json
from classStore.server.dataLab import SQLFun

class ListTable():
  def __init__(self):
    print('success use ListTable');
    data = request.get_data();
    self.data = data;
  def getTree(self, config):
    print('This is the getTree');
    conn = config.connection();
    cursor = conn.cursor();

    treeSQL = SQLFun('*', 'listtable');

    sqlData = treeSQL.search()
    cursor.execute(sqlData)
    resultData = cursor.fetchall();

    initTree = [];
    conn.commit();

    for i in range(len(resultData)):
      item = resultData[i]
      isLeaf = False if item[2] == 1 else True

      if (item[3] == 0):
        loopData = {
          'key': item[0],
          'title': item[1],
          'isLeaf': isLeaf,
          'children': []
        }
        initTree.append(loopData)
        continue
      else:
        for j in range(len(initTree)):
          initTreeData = initTree[j]
          if (item[3] == initTreeData['key']):
            childData = {
              'key': item[0],
              'title': item[1],
              'isLeaf': isLeaf
            }
            initTreeData['children'].append(childData)
          continue
        continue
    return json.dumps(initTree);

  def listInfor(self, config):
    print('This is the listInfor');
    ids = request.args.get('id')

    conn = config.connection();
    cursor = conn.cursor();
    
    inforSQL = SQLFun('describeInfor', 'listtable');
    sqlData = inforSQL.select('id');

    # cursor.execute(sqlData, ids)
    cursor.execute(sqlData+ids);

    rowDescribe =  cursor.fetchall();

    print(rowDescribe);

    conn.commit();

    backDescribe = rowDescribe[0][0]

    cursor.close();
    conn.close();

    res = {};
    res['describe'] = backDescribe
    print(res)
    return json.dumps(res);




    
