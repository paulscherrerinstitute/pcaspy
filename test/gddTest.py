import pcaspy

s = pcaspy.gdd()
s.put("sdcsd")
print s.primitiveType(), s.get()


s.put(12)
print s.primitiveType(), s.get()


s.put("sdcsd")
print s.get()

s.put(12)
print s.primitiveType(), s.get()

s.setPrimType(pcaspy.aitEnumString)
s.put(["sdcsd","sdcsd"])
print s.primitiveType(), s.get()

s.put(range(12))
print s.get()

t=s

print t.get()

del s


t.put(range(15))
print t.get()

del t
