"""Focused checks for the System One request and conservative verdict boundary."""

import json
from unittest import TestCase, main, mock

import eyeballs_optional as triage


class TriageTest(TestCase):
    def test_model_request_uses_typed_choice_and_optional_bearer(self):
        response = mock.MagicMock()
        response.__enter__.return_value = response
        response.read.return_value = b'{"answers": {}}'
        with mock.patch.object(triage, "urlopen", return_value=response) as open_url:
            self.assertEqual(triage.model_request("http://localhost:8000/v1/systemone", "secret", "local", {"diff": "example"}),
                             {"answers": {}})
        request = open_url.call_args.args[0]
        self.assertEqual(request.get_header("Authorization"), "Bearer secret")
        payload = json.loads(request.data)
        self.assertEqual(payload["model"], "local")
        self.assertEqual(payload["questions"]["classification"]["type"], "choice")
        self.assertIn("EO:internal_maintenance", payload["questions"]["classification"]["criteria"])

    def test_eo_requires_passed_gate_enabled_path_and_confidence(self):
        gates = {"gate_status": "passed", "policy": {"disabled_eo_paths": []}}
        answer = {"choice": "EO:internal_maintenance", "confidence": 0.95}
        self.assertEqual(triage.decide(gates, answer), "eyeballs optional (EO) candidate")
        gates["gate_status"] = "pending"
        self.assertEqual(triage.decide(gates, answer), "eyeballs required (ER)")
        gates["gate_status"] = "passed"
        gates["policy"]["disabled_eo_paths"] = ["internal_maintenance"]
        self.assertEqual(triage.decide(gates, answer), "eyeballs required (ER)")
        gates["policy"]["disabled_eo_paths"] = []
        answer["confidence"] = 0.89
        self.assertEqual(triage.decide(gates, answer), "eyeballs required (ER)")


if __name__ == "__main__":
    main()
