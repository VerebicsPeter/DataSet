# Patterns for matching on nodes

import redbaron as rb


for_to_list_comprehension = {
  "type" : rb.ForNode,
  "nodes": [
  {
    "type": rb.AtomtrailersNode,
    "nodes": [
    {
      "type": rb.NameNode, "nodes": []
    },
    {
      "type": rb.NameNode, "attr": [("value", "append")], "nodes": []
    },
    {
    "type": rb.CallNode, "nodes": [
      {
        "type": rb.CallArgumentNode, "nodes": "*"
      }]
    }]
  }]
}


for_to_list_comprehension_if = {
  "type" : rb.ForNode,
  "nodes": [
  {
    "type": rb.IfelseblockNode,
    "nodes": [
    {
      "type": rb.IfNode,
      "attr": [],
      "nodes": [
      {
        "type": rb.AtomtrailersNode,
        "nodes": [
        {
          "type": rb.NameNode, "nodes": []
        },
        {
          "type": rb.NameNode, "attr": [("value", "append")], "nodes": []
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


for_to_numpy_sum = {
  "type": rb.ForNode,
  "nodes": [
  {
    "type": rb.AssignmentNode, "attr": [('operator', '+')],
    "nodes": [
    {
      "type": rb.NameNode, "nodes": []
    }]
  }]
}
