# TODO: try to implement attribute value checks in these patterns

# Patterns for patter matching on nodes

import redbaron as rb


for_to_listc = {
  "type" : rb.ForNode,
  "nodes": [
  {
    "type": rb.AtomtrailersNode,
    "nodes": [
    {
      "type": rb.NameNode, "nodes": []
    },
    {
      "type": rb.NameNode, "nodes": []
    },
    {
    "type": rb.CallNode, "nodes": [
      {
        "type": rb.CallArgumentNode, "nodes": "*"
      }]
    }]
  }]
}


for_to_listc_if = {
  "type" : rb.ForNode,
  "nodes": [
  {
    "type": rb.IfelseblockNode,
    "nodes": [
    {
      "type": rb.IfNode,
      "nodes": [
      {
        "type": rb.AtomtrailersNode,
        "nodes": [
        {
          "type": rb.NameNode, "nodes": []
        },
        {
          "type": rb.NameNode, "nodes": []
        },
        {
          "type": rb.CallNode, "nodes": [
          {
            "type": rb.CallArgumentNode, "nodes": "*"
          }]
        }]
      }]
    }]
  }]
}

"""
sum = 0
for i in range(1, 20):
  sum += i
######################
sum = np.sum(range(1, 20)) #  if numpy is imported
"""

for_sum = {
  "type": rb.ForNode,
  "nodes": [
  {
    "type": rb.AssignmentNode,
    "nodes": [
    {
      "type": rb.NameNode, "nodes": []
    }]
  }]
}
