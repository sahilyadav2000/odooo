from odoo import models, fields, api

class ApprovalDashboard(models.Model):
    _name = 'approval.dashboard'
    _description = 'Approval Dashboard'

    name = fields.Char(default="Dashboard")

    total_requests = fields.Integer(compute='_compute_counts')
    approved = fields.Integer(compute='_compute_counts')
    rejected = fields.Integer(compute='_compute_counts')
    pending = fields.Integer(compute='_compute_counts')

    @api.depends()
    def _compute_counts(self):
        requests = self.env['approval.request']
        for rec in self:
            rec.total_requests = requests.search_count([])
            rec.approved = requests.search_count([('state', '=', 'approved')])
            rec.rejected = requests.search_count([('state', '=', 'rejected')])
            rec.pending = requests.search_count([('state', '=', 'confirmed')])