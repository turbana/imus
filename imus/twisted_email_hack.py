"""
Ugh.

When we send email notifications it's near the end of the crawler's life-cycle
after all scraping and processing has occurred. Because scrapy uses twisted the
mail handler creates a Defered to send the mail. Somehow the twisted reactor
(main loop) closes down before all the mail Defered's have processed, causing
in progress IO calls on a closed socket triggering an error. See this github
scrapy issue for more information, specifically Ksianka's comments:
https://github.com/scrapy/scrapy/issues/3478.

It appears to be related to the freeing of an underlying TLS socket within
twisted's TLSMemoryBIOProtocol object. See the following pull-request:
https://github.com/twisted/twisted/pull/955.

I don't want to manually touch twisted's source (not that this is much better),
so hot-patch twisted's code with a modified version of the offending function.
The only change is to comment out the freeing of the `_tls_connection` object.
"""

from twisted.protocols.policies import ProtocolWrapper
from twisted.protocols.tls import TLSMemoryBIOProtocol


def fixed_connectionLost(self, reason):
    """
    Handle the possible repetition of calls to this method (due to either
    the underlying transport going away or due to an error at the TLS
    layer) and make sure the base implementation only gets invoked once.
    """
    if not self._lostTLSConnection:
        # Tell the TLS connection that it's not going to get any more data
        # and give it a chance to finish reading.
        self._tlsConnection.bio_shutdown()
        self._flushReceiveBIO()
        self._lostTLSConnection = True
    reason = self._reason or reason
    self._reason = None
    self.connected = False
    ProtocolWrapper.connectionLost(self, reason)

    # Breaking reference cycle between self._tlsConnection and self.
    #self._tlsConnection = None


TLSMemoryBIOProtocol.connectionLost = fixed_connectionLost
