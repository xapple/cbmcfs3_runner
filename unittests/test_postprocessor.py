# Third party modules #
import pandas

# Internal modules #
from cbm_runner.steps.post_process import PostProcessor

# Constants #

###############################################################################
def test_classifiers_join():
    mock_parent = type('MockParent', (object,), {'parent_dir': '~/test/'})
    post_proc = PostProcessor(mock_parent)
    post_proc.database = {'asdfasdf': pandas.Dataframe('1,2,3'),
                          'ffasdfsa': pandas.Dataframe('1,2,3')}
    assert post_proc.classifiers == pandas.Dataframe('4,4,4')