# Patterns for matching on nodes

# 'attr'   is used to match child nodes with primitive values on a parent node (optional)
# 'target' is used to match the 'target' attribute on a node                   (optional)
# 'nodes'  is used to match nodes that have NodeList value


from redbaron.nodes import *


for_to_list_comprehension = {
  "type" : ForNode,
  "nodes": [
  {
    "type": AtomtrailersNode,
    "nodes": [
    {
      "type": NameNode, "nodes": []
    },
    {
      "type": NameNode, "attr": {"value":"append"}, "nodes": []
    },
    {
    "type": CallNode, "nodes": [
      {
        "type": CallArgumentNode, "nodes": "*"
      }]
    }]
  }]
}


for_to_list_comprehension_if = {
  "type" : ForNode,
  "nodes": [
  {
    "type": IfelseblockNode,
    "nodes": [
    {
      "type": IfNode,
      "nodes": [
      {
        "type": AtomtrailersNode,
        "nodes": [
        {
          "type": NameNode, "nodes": []
        },
        {
          "type": NameNode, "attr": {"value":"append"}, "nodes": []
        },
        {
          "type": CallNode, "nodes": [
          {
            "type": CallArgumentNode, "nodes": "*"
          }]
        }]
      }]
    }]
  }]
}


for_to_dict_comprehension = {
  "type": ForNode,
  "nodes": [
  {
    "type": AssignmentNode,
    "target": 
    {
      "type": AtomtrailersNode,
      "nodes": [
      {
        "type": NameNode, "nodes": []
      },
      {
        "type": GetitemNode, "nodes": "*"
      }]
    }, "nodes": "*"
  }]
}


for_to_dict_comprehension_if = {
  "type": ForNode,
  "nodes": [
  {
    "type": IfelseblockNode,
    "nodes": [
    {
      "type": IfNode,
      "nodes": [
      {
        "type": AssignmentNode,
        "target": 
        {
          "type": AtomtrailersNode,
          "nodes": [
            {
              "type": NameNode, "nodes": []
            },
            {
              "type": GetitemNode, "nodes": "*"
            }
          ]
        }, "nodes": "*"
      }]
    }]
  }]
}


for_to_numpy_sum = {
  "type": ForNode,
  "nodes": [
  {
    "type": AssignmentNode, "attr": {"operator":"+"},
    "nodes": [
    {
      "type": NameNode, "nodes": []
    }]
  }]
}

