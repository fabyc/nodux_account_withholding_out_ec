# -*- coding: utf-8 -*-
#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.

from trytond.model import Workflow, ModelSQL, ModelView, fields
from trytond.pool import PoolMeta, Pool
from trytond.pyson import Eval
from trytond.wizard import Wizard, StateTransition, StateView, Button
from trytond.transaction import Transaction
from trytond.wizard import Wizard, StateView, StateTransition, StateAction, \
    Button
from decimal import Decimal
from collections import defaultdict
from trytond import backend
from trytond.pyson import If, Eval, Bool, Id
from trytond.transaction import Transaction
from trytond.pool import Pool

__all__ = ['Invoice','ValidatedInvoice','WithholdingOutStart','WithholdingOut']
__metaclass__ = PoolMeta
#customer->cliente

class Invoice():
    'Invoice'
    __name__ = 'account.invoice'

    @classmethod
    def withholdingOut(cls, invoices):
        '''
        Withholding and return ids of new withholdings.
        Return the list of new invoice
        '''
        MoveLine = Pool().get('account.move.line')
        Withholding = Pool().get('account.withholding')
        return Withholding.withholdingOut(invoices)

class ValidatedInvoice(Wizard):
    'Validate Invoice'
    __name__ = 'account.invoice.validate_invoice'

    start = StateView('account.withholding',
        'nodux_account_withholding_ec.withholding_view_form', [
            Button('Cerrar', 'end', 'tryton-ok', default=True),
            ])

    def default_start(self, fields):

        Invoice = Pool().get('account.invoice')
        Journal = Pool().get('account.journal')

        default = {}
        journals = Journal.search([('type', '=', 'expense')])
        for j in journals:
            journal = j

        invoice = Invoice(Transaction().context.get('active_id'))

        invoice.set_number()
        #invoice.create_move()

        pool = Pool()
        Date = pool.get('ir.date')
        fecha_actual = Date.today()
        Taxes = pool.get('account.tax')
        taxes_1 = Taxes.search([('type', '=', 'percentage')])
        Configuration = pool.get('account.configuration')

        if Configuration(1).default_account_withholding:
            w = Configuration(1).default_account_withholding
        else:
            self.raise_user_error('No ha configurado la cuenta por defecto para la retencion. \nDirijase a Financiero-Configuracion-Configuracion Contable')

        if invoice.type == 'out_invoice':
            default['type'] = 'out_withholding'
        if invoice.reference:
            default['number_w'] = invoice.reference

        default['account'] = j.id
        default['withholding_address'] = invoice.invoice_address.id
        default['description'] = invoice.description
        default['reference'] = invoice.number
        default['comment']=invoice.comment
        default['company']=invoice.company.id
        default['party']=invoice.party.id
        default['currency']=invoice.currency.id
        default['journal']= journal.id
        default['taxes']=[]
        default['base_imponible'] = invoice.taxes[0].base
        default['iva']= invoice.taxes[0].amount
        default['withholding_date']= fecha_actual
        return default

class WithholdingOutStart(ModelView):
    'Withholding Out Start'
    __name__ = 'nodux_account_withholding_ec.out_withholding.start'

class WithholdingOut(Wizard):
    'Withholding Out'
    __name__ = 'nodux_account_withholding_ec.out_withholding'
    #crear referencias:
    start = StateView('nodux_account_withholding_ec.out_withholding.start',
        'nodux_account_withholding_out_ec.out_withholding_start_view_form', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Withholding', 'withholdingOut', 'tryton-ok', default=True),
            ])
    withholdingOut = StateAction('nodux_account_withholding_out_ec.act_withholding_form')

    @classmethod
    def __setup__(cls):
        super(WithholdingOut, cls).__setup__()

    def do_withholdingOut(self, action):
        pool = Pool()
        Invoice = pool.get('account.invoice')

        invoices = Invoice.browse(Transaction().context['active_ids'])
        for invoice in invoices:
            if invoice.type != 'out_invoice':
                self.raise_user_error('No puede generar un comprobante de retencion de cliente desde Factura de Proveedor')

        out_withholding = Invoice.withholdingOut(invoices)

        data = {'res_id': [i.id for i in out_withholding]}
        if len(out_withholding) == 1:
            action['views'].reverse()

        return action, data
