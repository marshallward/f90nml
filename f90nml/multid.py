"""f90nml.multiD
   =============

   Handles multi-dimensional arrays in fortran namelists

   :copyright: Copyright 2015 Marshall Ward, see AUTHORS for details.
   :license: Apache License, Version 2.0, see LICENSE for details.
"""

class multi_index:
  """ This is a multi-dimensional column-major iterator.
      Each call to ``next`` returns a tuple of indexes that is
      ``dim`` long."""
    
  def __init__(self,idx):
    self.index = []
    self.current = []
    self.length = []
    self.dim = 0
    for d in idx:
      self.index.append(list(d))
      self.current.append(-1)
      self.length.append(len(self.index[-1]))

    self.dim = len(idx)

  def incr_dim(self,d):
    try:
      self.current[d] += 1
      if self.current[d] == self.length[d]:
          self.current[d] = 0
          self.incr_dim(d+1)
    except IndexError:
      raise StopIteration

  def next(self):
    # res = self.next_help(self.index,self.iterator)
    # print "final:",res
    res = []
    self.incr_dim(0)
    for d in xrange(self.dim):
      res.append(self.index[d][self.current[d]])

    return tuple(res)


class multi_value:
  """ This class manages a multi-dimensional array """

  def __init__(self,e):
    self.values = self.grow(e)

  def grow(self,e):
    if e: return [ self.grow(e[1:]) for i in range(e[0]-1) ]

  def get_help(self,value,idx):
    if len(idx) > 1: 
      return self.get_help( value[idx[0]],idx[1:] )
    else:
      return value[idx[0]]

  def __getitem__(self,idx):
    return self.get_help(self.values,idx)

  def set_help(self,values,idx,val):
    if len(idx) > 1:
      self.set_help( values[idx[0]],idx[1:],val)
    else:
      values[idx[0]] = val

  def __setitem__(self,idx,val):
    self.set_help(self.values,idx,val)

      # print e
    #
    # def append_value(self,value,ix,v):
    #   if ix: 
    #     self.append_value(value[ix[0]],ix[1:],v)
    #   else:
    #     value = v
    #
    # def add_values(self,idx,values):
    #   self.gen_index_list(idx)
    #   for v in values:
    #     ix = self.next_index()
    #     self.append_value(self.values,ix,v)
    #



