#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import unittest
from parlai.core.params import ParlaiParser
import parlai.utils.testing as testing_utils

"""
Integration tests for the Self-Feeding chatbot project.

See projects/self_feeding.
"""

from parlai.tasks.self_feeding.agents import AllTeacher


@testing_utils.skipUnlessGPU
class TestSelffeeding(unittest.TestCase):
    def test_dataset_integrity(self):
        """
        Check the controllable dialogue data loads.
        """
        pp = ParlaiParser(True, False)
        opt = pp.parse_kwargs(task='self_feeding:all', datatype='train:ordered')
        teacher = AllTeacher(opt)
        assert teacher.num_examples() == 193777
        assert teacher.num_episodes() == 193777
        assert 'some cheetah chasing to stay in shape' in teacher.act()['text']

        opt['datatype'] = 'valid'
        teacher = AllTeacher(opt)
        assert teacher.num_examples() == 3500

        opt['datatype'] = 'test'
        teacher = AllTeacher(opt)
        assert teacher.num_examples() == 7801

    def test_train_model(self):
        """
        Check the training script doesn't crash.
        """
        opt = {
            'model': 'projects.self_feeding.self_feeding_agent:SelfFeedingAgent',
            'task': 'self_feeding:all',
            'max_train_time': 120,
            'dia_train': 'train_hh131k_hb60k.txt',
            'n_layers': 2,
            'n_heads': 2,
            'candidates': 'batch',
            'validation_metric': 'dia_acc',
            'optimizer': 'adamax',
            'learningrate': 0.0025,
            'ffn_size': 32,
            'batchsize': 32,
            'embeddings_scale': False,
        }
        testing_utils.train_model(opt)

    def test_released_model(self):
        """
        Check the pretrained model produces correct results.
        """
        _, test = testing_utils.eval_model(
            {
                'model_file': 'zoo:self_feeding/hh131k_hb60k_fb60k_st1k/model',
                'task': 'self_feeding:all',
                'batchsize': 20,
            },
            skip_valid=True,
        )

        self.assertAlmostEqual(test['dia_acc'], 0.506, delta=0.001)
        self.assertAlmostEqual(test['fee_acc'], 0.744, delta=0.001)
        self.assertAlmostEqual(test['sat_f1'], 0.8343, delta=0.0001)


if __name__ == '__main__':
    unittest.main()
