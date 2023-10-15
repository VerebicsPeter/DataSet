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
