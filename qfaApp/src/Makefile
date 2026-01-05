TOP=../..

include $(TOP)/configure/CONFIG
#----------------------------------------
#  ADD MACRO DEFINITIONS AFTER THIS LINE
#=============================

#=============================
# Build the IOC application

PROD_IOC = qfa
# pdu.dbd will be created and installed
DBD += qfa.dbd

# pdu.dbd will be made up from these files:
qfa_DBD += base.dbd

# Include dbd files from all support applications:
qfa_DBD += pscCore.dbd

# Add all the support libraries needed by this IOC
qfa_LIBS += pscCore 

# pdu_registerRecordDeviceDriver.cpp derives from pdu.dbd
qfa_SRCS += qfa_registerRecordDeviceDriver.cpp

# Build the main IOC entry point on workstation OSs.
qfa_SRCS_DEFAULT += qfaMain.cpp
qfa_SRCS_vxWorks += -nil-

# Add support from base/src/vxWorks if needed
#pdu_OBJS_vxWorks += $(EPICS_BASE_BIN)/vxComLibrary

# Finally link to the EPICS Base libraries
qfa_LIBS += $(EPICS_BASE_IOC_LIBS)

#===========================

include $(TOP)/configure/RULES
#----------------------------------------
#  ADD RULES AFTER THIS LINE

