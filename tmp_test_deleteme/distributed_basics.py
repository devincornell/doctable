#!/usr/bin/env python
# coding: utf-8

# # `Distribute` Parallel Processing Basics
# Due to a number of limitations involving data passed to processes using `multiprocessing.Pool()`, I've implemented a similar class called `Distribute()`. The primary difference is that Distribute is meant to distribute chunks of data for parallel processing, so your map function should parse multiple values. There are currently two functions in Distribute:
# 
# * `.map_chunk()` simply applies a function to a list of elements and returns a list of parsed elements.
# * `.map()` applies a function to a single element. Same as `multiprocessing.Pool().map()`.

# In[1]:


#from IPython import get_ipython
import sys
sys.path.append('..')
import doctable


# ## `.map()` Method
# Unsurprisingly, this method works exactly like the `multiprocessing.Pool().map()`. Simply provide a sequence of elements and a function to apply to them, and this method will parse all the elements in parallel.

# In[2]:


def multiply(x, y=2):
    return x * y

nums = list(range(5))
with doctable.Distribute(3) as d:
    res = d.map(multiply, nums)
    print(res)
    
    # pass any argument to your function here.
    # we try multiplying by 5 instead of 2.
    res = d.map(multiply, nums, 5)
    print(res)


# ## `.map_chunk()` Method
# Allows you to write map functions that processes a chunk of your data at a time. This is the lowest-level method for distributed processing.

# In[3]:


# map function to multiply 1.275 by each num and return a list
def multiply_nums(nums):
    return [num*1.275 for num in nums]

# use Distribute(3) to create three separate processes
nums = list(range(1000))
with doctable.Distribute(3) as d:
    res = d.map_chunk(multiply_nums, nums)

# won't create new process at all. good for testing
with doctable.Distribute(1) as d:
    res = d.map_chunk(multiply_nums, nums)
res[:3]

