#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
from trytond.pool import Pool
from .invoice import *
from .account import *
from .withholding import *
from .move import *

def register():
    Pool.register(
        FiscalYear,
        Period,
        Configuration,
        Invoice,
        WithholdingOutStart,
        Move,
        AccountWithholding,
        AccountWithholdingTax,
        module='nodux_account_withholding_out_ec', type_='model')
    Pool.register(
        WithholdingOut,
        ValidatedInvoice,
        module='nodux_account_withholding_out_ec', type_='wizard')
    
