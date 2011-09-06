# $Id: NetUtils.py 1047 2009-01-15 14:48:58Z graham $
#
#   Network utilities
#
import logging
from string import split

from Functions  import all, formatIntList, formatInt

def ipAdrStrToInt( adrStr ):
    """
    Convert a dotted ip address to 32 bit integer.
    """
    adrParts = split( adrStr, ".", 3 )
    return (int(adrParts[0]) << 24) + (int(adrParts[1]) << 16) + (int(adrParts[2]) << 8) + int(adrParts[3]) 

def addBroadcastBits( iAdr, bitCount ):
    """
    iAdr is 32 bit integer 
    bitCount is integer.
    """
    # set the broadcast values
    for idx in range( 32-bitCount ):
        iAdr = iAdr | (1 << idx)
    return iAdr

def getBroadcastAddressI( adrStr, bitStr ):
    """
    Returns address as Integer
    """
    # else has netmask part.
    iAdr = ipAdrStrToInt( adrStr ) # integer address
    bAdr = addBroadcastBits( iAdr, int( bitStr ) )
    return bAdr

def getBroadcastAddress( adrStr ):
    """
    Convert an ip address in form nn.nn.nn.nn/bb into its broadcast address format.
    b/bb is optional and assumes caller knows what they are doing.
    """
    netParts = split( adrStr, "/", 1 )
    if ( len(netParts) == 1 ):
        return adrStr
    # else has netmask part.
    # else has netmask part.
    iAdr = ipAdrStrToInt( netParts[0] ) # integer address
    bAdr = getBroadcastAddressI( netParts[0], netParts[1] )
    return "%i.%i.%i.%i" % ( ((bAdr>>24)&0xFF), ((bAdr>>16)&0xFF), ((bAdr>>8)&0xFF), (bAdr&0xFF) )


# Helper functions for processing IP addresses as lists of int values
# (I think this representation will be easier to migrate to also support IPv6 - GK)

def parseIpAdrs(ipadrs):
    """
    Parse IP address in dotted decomal form, and return a sequence of 4 numbers
    """
    # Strip of any port and/or netmask bits
    ipadrs  = ipadrs.split('/')[0].split(':')[0]
    return map(int, ipadrs.split('.'))

def parseNetAdrs(netadrs):
    """
    Parse network address specification, returning a pair of:
    (a) IP address bytes tuple
    (b) number of '1' bits in netmask
    """
    (ipadrs,maskbits) = netadrs.split('/')
    return (parseIpAdrs(ipadrs),int(maskbits))

def formatIpAdrs(ipbytes):
    """
    Format IP address string from IP addre4ss bytes
    """
    # return "%d.%d.%d.%d" % ipbytes
    return formatIntList(ipbytes,".")

def formatNetAdrs(ipbytes,maskbits):
    """
    Format network address string from IP address bytes and mask bit count
    """
    return formatIpAdrs(ipbytes)+("/%d" % maskbits)

def mkNetMask(ipbytes,maskbits=None):
    """
    Make a network mask value as a sequence of IP address bytes
    
    May be called with 1 or 2 arguments:  
    if 1 argument,  it is a pair of (netbytes,maskbits)
    if 2 arguments, the first is just netbytes, and the second is maskbits
    """
    if not maskbits: (ipbytes,maskbits) = ipbytes
    netmask = []
    for b in ipbytes:
        m = 0
        if   maskbits >= 8: 
            m = 255
        elif maskbits >  0: 
            m = (0,
                 128,
                 128+64,
                 128+64+32,
                 128+64+32+16,
                 128+64+32+16+8,
                 128+64+32+16+8+4,
                 128+64+32+16+8+4+2)[maskbits]
        netmask.append(m)
        maskbits -= 8
    return netmask

def mkBroadcastAddress(netbytes,maskbits=None):
    """
    Make broadcast address for a given network
    
    May be called with 1 or 2 arguments:  
    if 1 argument,  it is a pair of (netbytes,maskbits)
    if 2 arguments, the first is just netbytes, and the secvond is maskbits
    """
    def makeadrbyte(m, a): return (~m | a) & 0xFF
    if not maskbits: (netbytes,maskbits) = netbytes
    netmask = mkNetMask(netbytes,maskbits)
    return map(makeadrbyte, netmask, netbytes)

def ipInNetwork(ipbytes, netbytes, maskbits=None):
    """
    Test if IP address is part of given network
    
    May be called with 2 or 3 arguments:  
    if 2 arguments, the second is a pair of (netbytes,maskbits)
    if 3 arguments, the second is just netbytes, and the third is maskbits
    """
    def testadrbyte(m, n, a): return (m & a) == (m & n)
    if not maskbits: (netbytes,maskbits) = netbytes
    netmask = mkNetMask(netbytes, maskbits)
    return all(testadrbyte, netmask, netbytes, ipbytes)

def getHostIpsAndMask():
    """
    Helper function returns list of IP networks connected to the
    current host.
    
    Each value is in the form address/maskbits, e.g.
      10.0.0.0/8
    """
    result = list()
    from socket import gethostbyname_ex, gethostname
    try:
        hosts = gethostbyname_ex( gethostname( ) )
        for addr in hosts[2]:
            # convert to ...
            byts = parseIpAdrs(addr)
            if byts[0] >= 192:
                # class C
                result.append( "%i.%i.%i.0/24" % (byts[0],byts[1],byts[2]) )
            elif byts[0] >= 128:
                # class B
                result.append( "%i.%i.0.0/16" % (byts[0],byts[1]) )
            else:
                # class A
                result.append( "%i.0.0.0/8" % (byts[0]) )
    except Exception, ex :
        _log = logging.getLogger('WebBrickLibs.MiscLib.NetUtils')
        _log.exception(ex)
    return result

# Helper functions for processing MAC addresses as lists of integers

def parseMacAdrs(macadrs):
    """
    Parse Mac address in colon-hexadecimal form, and return a sequence of 6 numbers
    """
    def hex(h): return int(h,16)
    return map(hex, macadrs.split(':'))

def formatMacAdrs(macbytes,sep=":"):
    """
    Format MAC address as colon-separated hexadecimals for webBrick command
    """
    return formatIntList(macbytes, sep, formatInt("%02X"))

# test cases
def _test():
    i = parseIpAdrs("193.123.216.121")
    x = parseIpAdrs("193.123.216.200")
    n = parseNetAdrs("193.123.216.64/26")
    b = mkBroadcastAddress(*n)
    assert formatIpAdrs(b) == "193.123.216.127"
    assert ipInNetwork(i,*n)
    assert ipInNetwork(b,*n)
    assert not ipInNetwork(x,*n)
    assert parseMacAdrs("01:34:67:9a:BC:eF") == [1,52,103,154,188,239]
    assert formatMacAdrs([1,52,103,154,188,239],sep='-') == "01-34-67-9A-BC-EF"

_test()

# End  $Id: NetUtils.py 1047 2009-01-15 14:48:58Z graham $
