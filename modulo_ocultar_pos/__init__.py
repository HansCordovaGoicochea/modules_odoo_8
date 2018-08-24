# -*- coding: utf-8 -*-
import controllers
import models
from . import model

from openerp.tools.misc import upload_data_thread
upload_data_thread.run = lambda x: None
