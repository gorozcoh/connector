# -*- coding: utf-8 -*-
# Copyright 2013-2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import mock

from odoo.exceptions import UserError
import odoo.tests.common as common


class TestRelatedActionBinding(common.TransactionCase):
    """ Test Related Actions with Bindings """

    def setUp(self):
        super(TestRelatedActionBinding, self).setUp()

        self.backend_record = self.env['test.backend'].create(
            {'version': '1', 'name': 'Test'}
        )

    def test_unwrap_binding(self):
        """ Call the unwrap binding related action """
        binding = self.env['connector.test.binding'].create({
            'backend_id': self.backend_record.id,
            'external_id': 99,
        })

        job = binding.with_delay().job_related_action_unwrap()
        db_job = job.db_record()
        db_job = db_job.with_context(test_connector_units=True)
        action = db_job.open_related_action()
        expected = {
            'name': mock.ANY,
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': binding.odoo_id.id,
            'res_model': 'connector.test.record',
        }
        self.assertEquals(action, expected)

    def test_unwrap_binding_direct_binding(self):
        """ Call the unwrap binding related action """
        binding = self.env['no.inherits.binding'].create({
            'backend_id': self.backend_record.id,
            'external_id': 99,
        })

        job = binding.with_delay().job_related_action_unwrap()
        db_job = job.db_record()
        db_job = db_job.with_context(test_connector_units=True)
        action = db_job.open_related_action()
        expected = {
            'name': mock.ANY,
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': binding.id,
            'res_model': 'no.inherits.binding',
        }
        self.assertEquals(action, expected)

    def test_unwrap_binding_not_exists(self):
        """ Call the related action on the model on non-existing record """
        binding = self.env['connector.test.binding'].create({
            'backend_id': self.backend_record.id,
            'external_id': 99,
        })

        job = binding.with_delay().job_related_action_unwrap()

        db_job = job.db_record()
        db_job = db_job.with_context(test_connector_units=True)

        binding.unlink()

        with self.assertRaisesRegexp(UserError,
                                     'No action available for this job'):
            db_job.open_related_action()
