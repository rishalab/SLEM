import time

def sleep():
    time.sleep(30)
    
###------------------------------------------###

# Handling missing data 

def isna(df, cname):
    return df[cname].isna()


def dropna(df):
    return df.dropna()


def fillna(df, val):
    return df.fillna(val)


###------------------------------------------###

# Table operations
# drop column
# groupby
# sort

def drop(df, cnameArray):
    return df.drop(columns=cnameArray)


def groupby(df, cname):
    return df.groupby(cname)


def sort(df, cname):
    return df.sort_values(by=[cname])

###--------------------------------------------###
# Statistical Operations
# min, max, mean, count, unique, sum

# count 

def count(df):
    return df.count()

# sum

def sum(df, cname):
    return df[cname].sum()

# mean

def mean(df):
    return df.mean()

# min

def min(df):
    return df.min()
# max

def max(df):
    return df.max()

# unique

def unique(df):
    return df.unique()