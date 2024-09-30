/*
 * bbTest.c
 *
 * Academic License - for use in teaching, academic research, and meeting
 * course requirements at degree granting institutions only.  Not for
 * government, commercial, or other organizational use.
 *
 * Code generation for model "bbTest".
 *
 * Model version              : 1.1
 * Simulink Coder version : 9.7 (R2022a) 13-Nov-2021
 * C source code generated on : Thu Apr 18 12:21:40 2024
 *
 * Target selection: ert.tlc
 * Note: GRT includes extra infrastructure and instrumentation for prototyping
 * Embedded hardware selection: ARM Compatible->ARM Cortex
 * Code generation objectives: Unspecified
 * Validation result: Not run
 */

#include "bbTest.h"
#include "bbTest_types.h"
#include "rtwtypes.h"
#include "MW_I2C.h"
#include "bbTest_private.h"
#include "bbTest_dt.h"

/* Block signals (default storage) */
B_bbTest_T bbTest_B;

/* Block states (default storage) */
DW_bbTest_T bbTest_DW;

/* Real-time model */
static RT_MODEL_bbTest_T bbTest_M_;
RT_MODEL_bbTest_T *const bbTest_M = &bbTest_M_;

/* Forward declaration for local functions */
static void bbTest_SystemCore_setup(beagleboneblue_bbblueMPU9250__T *obj);
static void bbTest_SystemCore_setup(beagleboneblue_bbblueMPU9250__T *obj)
{
  MW_I2C_Mode_Type ModeType;
  uint32_T i2cname;
  obj->isInitialized = 1;
  MW_IMU_DMP_isAccel_Calibrated();
  MW_IMU_DMP_isGyro_Calibrated();
  MW_IMU_DMP_isMag_Calibrated();
  ModeType = MW_I2C_MASTER;
  i2cname = 2;
  obj->i2cObjmpu.MW_I2C_HANDLE = MW_I2C_Open(i2cname, ModeType);
  obj->i2cObjmpu.BusSpeed = 100000U;
  MW_I2C_SetBusSpeed(obj->i2cObjmpu.MW_I2C_HANDLE, obj->i2cObjmpu.BusSpeed);
  ModeType = MW_I2C_MASTER;
  i2cname = 2;
  obj->i2cObjak8963.MW_I2C_HANDLE = MW_I2C_Open(i2cname, ModeType);
  obj->i2cObjak8963.BusSpeed = 100000U;
  MW_I2C_SetBusSpeed(obj->i2cObjak8963.MW_I2C_HANDLE, obj->i2cObjak8963.BusSpeed);
  MW_Init_IMU_DMP(200);
  obj->TunablePropsChanged = false;
}

/* Model step function */
void bbTest_step(void)
{
  real_T gdata[3];

  /* MATLABSystem: '<Root>/MPU9250' */
  if (bbTest_DW.obj.SampleTime != bbTest_P.MPU9250_SampleTime) {
    bbTest_DW.obj.SampleTime = bbTest_P.MPU9250_SampleTime;
  }

  if (bbTest_DW.obj.TunablePropsChanged) {
    bbTest_DW.obj.TunablePropsChanged = false;
  }

  MW_Read_Accel(&bbTest_B.MPU9250_o1[0]);
  gdata[0] = 0.0;
  gdata[1] = 0.0;
  gdata[2] = 0.0;
  MW_Read_Gyro(&gdata[0]);
  gdata[0] = 0.0;
  gdata[1] = 0.0;
  gdata[2] = 0.0;
  MW_Read_Mag(&gdata[0]);

  /* MATLABSystem: '<Root>/MPU9250' */
  bbTest_B.MPU9250_o4[0] = 0.0;
  bbTest_B.MPU9250_o4[1] = 0.0;
  bbTest_B.MPU9250_o4[2] = 0.0;
  bbTest_B.MPU9250_o4[3] = 0.0;

  /* MATLABSystem: '<Root>/MPU9250' */
  MW_Read_Quat(&bbTest_B.MPU9250_o4[0]);

  /* External mode */
  rtExtModeUploadCheckTrigger(1);

  {                                    /* Sample time: [0.1s, 0.0s] */
    rtExtModeUpload(0, (real_T)bbTest_M->Timing.taskTime0);
  }

  /* signal main to stop simulation */
  {                                    /* Sample time: [0.1s, 0.0s] */
    if ((rtmGetTFinal(bbTest_M)!=-1) &&
        !((rtmGetTFinal(bbTest_M)-bbTest_M->Timing.taskTime0) >
          bbTest_M->Timing.taskTime0 * (DBL_EPSILON))) {
      rtmSetErrorStatus(bbTest_M, "Simulation finished");
    }

    if (rtmGetStopRequested(bbTest_M)) {
      rtmSetErrorStatus(bbTest_M, "Simulation finished");
    }
  }

  /* Update absolute time for base rate */
  /* The "clockTick0" counts the number of times the code of this task has
   * been executed. The absolute time is the multiplication of "clockTick0"
   * and "Timing.stepSize0". Size of "clockTick0" ensures timer will not
   * overflow during the application lifespan selected.
   * Timer of this task consists of two 32 bit unsigned integers.
   * The two integers represent the low bits Timing.clockTick0 and the high bits
   * Timing.clockTickH0. When the low bit overflows to 0, the high bits increment.
   */
  if (!(++bbTest_M->Timing.clockTick0)) {
    ++bbTest_M->Timing.clockTickH0;
  }

  bbTest_M->Timing.taskTime0 = bbTest_M->Timing.clockTick0 *
    bbTest_M->Timing.stepSize0 + bbTest_M->Timing.clockTickH0 *
    bbTest_M->Timing.stepSize0 * 4294967296.0;
}

/* Model initialize function */
void bbTest_initialize(void)
{
  /* Registration code */

  /* initialize real-time model */
  (void) memset((void *)bbTest_M, 0,
                sizeof(RT_MODEL_bbTest_T));
  rtmSetTFinal(bbTest_M, 10.0);
  bbTest_M->Timing.stepSize0 = 0.1;

  /* External mode info */
  bbTest_M->Sizes.checksums[0] = (1614519464U);
  bbTest_M->Sizes.checksums[1] = (872303843U);
  bbTest_M->Sizes.checksums[2] = (2005266068U);
  bbTest_M->Sizes.checksums[3] = (2977459242U);

  {
    static const sysRanDType rtAlwaysEnabled = SUBSYS_RAN_BC_ENABLE;
    static RTWExtModeInfo rt_ExtModeInfo;
    static const sysRanDType *systemRan[2];
    bbTest_M->extModeInfo = (&rt_ExtModeInfo);
    rteiSetSubSystemActiveVectorAddresses(&rt_ExtModeInfo, systemRan);
    systemRan[0] = &rtAlwaysEnabled;
    systemRan[1] = &rtAlwaysEnabled;
    rteiSetModelMappingInfoPtr(bbTest_M->extModeInfo,
      &bbTest_M->SpecialInfo.mappingInfo);
    rteiSetChecksumsPtr(bbTest_M->extModeInfo, bbTest_M->Sizes.checksums);
    rteiSetTPtr(bbTest_M->extModeInfo, rtmGetTPtr(bbTest_M));
  }

  /* block I/O */
  (void) memset(((void *) &bbTest_B), 0,
                sizeof(B_bbTest_T));

  /* states (dwork) */
  (void) memset((void *)&bbTest_DW, 0,
                sizeof(DW_bbTest_T));

  /* data type transition information */
  {
    static DataTypeTransInfo dtInfo;
    (void) memset((char_T *) &dtInfo, 0,
                  sizeof(dtInfo));
    bbTest_M->SpecialInfo.mappingInfo = (&dtInfo);
    dtInfo.numDataTypes = 19;
    dtInfo.dataTypeSizes = &rtDataTypeSizes[0];
    dtInfo.dataTypeNames = &rtDataTypeNames[0];

    /* Block I/O transition table */
    dtInfo.BTransTable = &rtBTransTable;

    /* Parameters transition table */
    dtInfo.PTransTable = &rtPTransTable;
  }

  /* Start for MATLABSystem: '<Root>/MPU9250' */
  bbTest_DW.obj.isInitialized = 0;
  bbTest_DW.obj.i2cObjmpu.DefaultMaximumBusSpeedInHz = 400000.0;
  bbTest_DW.obj.i2cObjmpu.isInitialized = 0;
  bbTest_DW.obj.i2cObjmpu.matlabCodegenIsDeleted = false;
  bbTest_DW.obj.i2cObjak8963.DefaultMaximumBusSpeedInHz = 400000.0;
  bbTest_DW.obj.i2cObjak8963.isInitialized = 0;
  bbTest_DW.obj.i2cObjak8963.matlabCodegenIsDeleted = false;
  bbTest_DW.obj.matlabCodegenIsDeleted = false;
  bbTest_DW.objisempty = true;
  bbTest_DW.obj.SampleTime = bbTest_P.MPU9250_SampleTime;
  bbTest_SystemCore_setup(&bbTest_DW.obj);
}

/* Model terminate function */
void bbTest_terminate(void)
{
  h_beagleboneblue_bbblueI2CMas_T *obj_0;
  i_beagleboneblue_bbblueI2CMas_T *obj;

  /* Terminate for MATLABSystem: '<Root>/MPU9250' */
  if (!bbTest_DW.obj.matlabCodegenIsDeleted) {
    bbTest_DW.obj.matlabCodegenIsDeleted = true;
  }

  obj = &bbTest_DW.obj.i2cObjak8963;
  if (!obj->matlabCodegenIsDeleted) {
    obj->matlabCodegenIsDeleted = true;
    if (obj->isInitialized == 1) {
      obj->isInitialized = 2;
    }
  }

  obj_0 = &bbTest_DW.obj.i2cObjmpu;
  if (!obj_0->matlabCodegenIsDeleted) {
    obj_0->matlabCodegenIsDeleted = true;
    if (obj_0->isInitialized == 1) {
      obj_0->isInitialized = 2;
    }
  }

  /* End of Terminate for MATLABSystem: '<Root>/MPU9250' */
}
