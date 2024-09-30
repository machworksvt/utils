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
 * C source code generated on : Wed Apr 17 22:25:23 2024
 *
 * Target selection: grt.tlc
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
#include "rt_nonfinite.h"

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
  real_T rtb_MPU9250_o4[4];
  real_T adata[3];

  /* MATLABSystem: '<Root>/MPU9250' */
  if (bbTest_DW.obj.SampleTime != bbTest_P.MPU9250_SampleTime) {
    bbTest_DW.obj.SampleTime = bbTest_P.MPU9250_SampleTime;
  }

  if (bbTest_DW.obj.TunablePropsChanged) {
    bbTest_DW.obj.TunablePropsChanged = false;
  }

  MW_Read_Accel(&adata[0]);
  adata[0] = 0.0;
  adata[1] = 0.0;
  adata[2] = 0.0;
  MW_Read_Gyro(&adata[0]);
  adata[0] = 0.0;
  adata[1] = 0.0;
  adata[2] = 0.0;
  MW_Read_Mag(&adata[0]);
  rtb_MPU9250_o4[0] = 0.0;
  rtb_MPU9250_o4[1] = 0.0;
  rtb_MPU9250_o4[2] = 0.0;
  rtb_MPU9250_o4[3] = 0.0;
  MW_Read_Quat(&rtb_MPU9250_o4[0]);

  /* End of MATLABSystem: '<Root>/MPU9250' */

  /* Matfile logging */
  rt_UpdateTXYLogVars(bbTest_M->rtwLogInfo, (&bbTest_M->Timing.taskTime0));

  /* signal main to stop simulation */
  {                                    /* Sample time: [0.1s, 0.0s] */
    if ((rtmGetTFinal(bbTest_M)!=-1) &&
        !((rtmGetTFinal(bbTest_M)-bbTest_M->Timing.taskTime0) >
          bbTest_M->Timing.taskTime0 * (DBL_EPSILON))) {
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

  /* initialize non-finites */
  rt_InitInfAndNaN(sizeof(real_T));

  /* initialize real-time model */
  (void) memset((void *)bbTest_M, 0,
                sizeof(RT_MODEL_bbTest_T));
  rtmSetTFinal(bbTest_M, 10.0);
  bbTest_M->Timing.stepSize0 = 0.1;

  /* Setup for data logging */
  {
    static RTWLogInfo rt_DataLoggingInfo;
    rt_DataLoggingInfo.loggingInterval = (NULL);
    bbTest_M->rtwLogInfo = &rt_DataLoggingInfo;
  }

  /* Setup for data logging */
  {
    rtliSetLogXSignalInfo(bbTest_M->rtwLogInfo, (NULL));
    rtliSetLogXSignalPtrs(bbTest_M->rtwLogInfo, (NULL));
    rtliSetLogT(bbTest_M->rtwLogInfo, "tout");
    rtliSetLogX(bbTest_M->rtwLogInfo, "");
    rtliSetLogXFinal(bbTest_M->rtwLogInfo, "");
    rtliSetLogVarNameModifier(bbTest_M->rtwLogInfo, "rt_");
    rtliSetLogFormat(bbTest_M->rtwLogInfo, 4);
    rtliSetLogMaxRows(bbTest_M->rtwLogInfo, 0);
    rtliSetLogDecimation(bbTest_M->rtwLogInfo, 1);
    rtliSetLogY(bbTest_M->rtwLogInfo, "");
    rtliSetLogYSignalInfo(bbTest_M->rtwLogInfo, (NULL));
    rtliSetLogYSignalPtrs(bbTest_M->rtwLogInfo, (NULL));
  }

  /* states (dwork) */
  (void) memset((void *)&bbTest_DW, 0,
                sizeof(DW_bbTest_T));

  /* Matfile logging */
  rt_StartDataLoggingWithStartTime(bbTest_M->rtwLogInfo, 0.0, rtmGetTFinal
    (bbTest_M), bbTest_M->Timing.stepSize0, (&rtmGetErrorStatus(bbTest_M)));

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
