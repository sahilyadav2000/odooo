from odoo import models, fields

class RejectWizard(models.TransientModel):
    _name = 'reject.wizard'

    reason = fields.Text()

    def action_confirm(self):
        request = self.env['approval.request'].browse(self._context.get('active_id'))
        request.state = 'rejected'
        request.reject_reason = self.reason