# -*- coding: utf-8 -*-
from dotenv import load_dotenv, find_dotenv

from .api import *
from .bot_general import *
from .database import *
from .channels import *

if __name__ == '__main__':
    pass
else:
    load_dotenv(find_dotenv())
