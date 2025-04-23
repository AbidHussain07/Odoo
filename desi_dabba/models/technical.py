from odoo import models,fields
from odoo.tools.safe_eval import safe_eval

class DesiDabbaTechnical(models.Model):
    _name = 'desi.dabba.technical'
    _description = "Technical Details"

    DEFAULT_ENV_VARIABLES = """
        # This dictionary contains default environment variables for the application. 
        # These variables define critical settings and configurations used during runtime, 
        # including database connections, API keys, and debug modes. 
        # Update these values cautiously to avoid disrupting the application's behavior.\n\n\n
        """
    model_id = fields.Many2one('ir.model',string="Model")
    code = fields.Text(string="Code")
    result = fields.Text(string="Result")

    def action_clear(self):
        self.code = ''
        self.result = ''

    def action_execute(self):
        try:
            if self.model_id:
                model = self.env[self.model_id.model]
            else:
                model = self
            self.result = eval(self.code.strip(),{'self':model})
        except Exception as e:
            self.result = str(e)
    