import sys
sys.path.append('scripts')
from m_prompt import *

test_prompt = mPrompt()
test_prompt.LoadPrompt('test/sakamata-in.txt')
test_prompt.TweakWeights("lighting, DeTaiL", 1.0, 0.5, 1.2)
test_prompt.Generate()
test_prompt.SavePrompt('test/sakamata-out.txt')
pass
