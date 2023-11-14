# Patterns for matching on nodes

# 'attr' is used to match child nodes with primitive values on a parent node (optional)
# 'target' is used to match the attribute 'target' on a node (optional)
# 'nodes' is used to match nodes that have NodeList value


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
      "type": rb.NameNode, "attr": {"value":"append"}, "nodes": []
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
      "nodes": [
      {
        "type": rb.AtomtrailersNode,
        "nodes": [
        {
          "type": rb.NameNode, "nodes": []
        },
        {
          "type": rb.NameNode, "attr": {"value":"append"}, "nodes": []
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


for_to_dict_comprehension = {
  "type": rb.ForNode,
  "nodes": [
  {
    "type": rb.AssignmentNode,
    "target": 
    {
      "type": rb.AtomtrailersNode,
      "nodes": [
      {
        "type": rb.NameNode, "nodes": []
      },
      {
        "type": rb.GetitemNode, "nodes": "*"
      }]
    }, "nodes": "*"
  }]
}


for_to_dict_comprehension_if = {
  "type": rb.ForNode,
  "nodes": [
  {
    "type": rb.IfelseblockNode,
    "nodes": [
    {
      "type": rb.IfNode,
      "nodes": [
      {
        "type": rb.AssignmentNode,
        "target": 
        {
          "type": rb.AtomtrailersNode,
          "nodes": [
            {
              "type": rb.NameNode, "nodes": []
            },
            {
              "type": rb.GetitemNode, "nodes": "*"
            }
          ]
        }, "nodes": "*"
      }]
    }]
  }]
}


for_to_numpy_sum = {
  "type": rb.ForNode,
  "nodes": [
  {
    "type": rb.AssignmentNode, "attr": {"operator":"+"},
    "nodes": [
    {
      "type": rb.NameNode, "nodes": []
    }]
  }]
}
