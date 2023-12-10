// Do NOT change. Changes will be lost next time file is generated

#define R__DICTIONARY_FILENAME RootDict

/*******************************************************************/
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#define G__DICTIONARY
#include "RConfig.h"
#include "TClass.h"
#include "TDictAttributeMap.h"
#include "TInterpreter.h"
#include "TROOT.h"
#include "TBuffer.h"
#include "TMemberInspector.h"
#include "TInterpreter.h"
#include "TVirtualMutex.h"
#include "TError.h"

#ifndef G__ROOT
#define G__ROOT
#endif

#include "RtypesImp.h"
#include "TIsAProxy.h"
#include "TFileMergeInfo.h"
#include <algorithm>
#include "TCollectionProxyInfo.h"
/*******************************************************************/

#include "TDataMember.h"

// Since CINT ignores the std namespace, we need to do so in this file.
namespace std {} using namespace std;

// Header files passed as explicit arguments
#include "flashggFinalFit/Background/interface/RooPowerLawSum.h"
#include "flashggFinalFit/Background/interface/WSTFileWrapper.h"
#include "flashggFinalFit/Background/interface/RooExponentialSum.h"
#include "flashggFinalFit/Background/interface/RooPowerLaw.h"
#include "flashggFinalFit/Background/interface/ProfileMultiplePdfs.h"
#include "flashggFinalFit/Background/interface/PdfModelBuilder.h"

// Header files passed via #pragma extra_include

namespace ROOT {
   static TClass *RooPowerLawSum_Dictionary();
   static void RooPowerLawSum_TClassManip(TClass*);
   static void *new_RooPowerLawSum(void *p = 0);
   static void *newArray_RooPowerLawSum(Long_t size, void *p);
   static void delete_RooPowerLawSum(void *p);
   static void deleteArray_RooPowerLawSum(void *p);
   static void destruct_RooPowerLawSum(void *p);

   // Function generating the singleton type initializer
   static TGenericClassInfo *GenerateInitInstanceLocal(const ::RooPowerLawSum*)
   {
      ::RooPowerLawSum *ptr = 0;
      static ::TVirtualIsAProxy* isa_proxy = new ::TIsAProxy(typeid(::RooPowerLawSum));
      static ::ROOT::TGenericClassInfo 
         instance("RooPowerLawSum", "interface/RooPowerLawSum.h", 26,
                  typeid(::RooPowerLawSum), ::ROOT::Internal::DefineBehavior(ptr, ptr),
                  &RooPowerLawSum_Dictionary, isa_proxy, 0,
                  sizeof(::RooPowerLawSum) );
      instance.SetNew(&new_RooPowerLawSum);
      instance.SetNewArray(&newArray_RooPowerLawSum);
      instance.SetDelete(&delete_RooPowerLawSum);
      instance.SetDeleteArray(&deleteArray_RooPowerLawSum);
      instance.SetDestructor(&destruct_RooPowerLawSum);
      return &instance;
   }
   TGenericClassInfo *GenerateInitInstance(const ::RooPowerLawSum*)
   {
      return GenerateInitInstanceLocal((::RooPowerLawSum*)0);
   }
   // Static variable to force the class initialization
   static ::ROOT::TGenericClassInfo *_R__UNIQUE_DICT_(Init) = GenerateInitInstanceLocal((const ::RooPowerLawSum*)0x0); R__UseDummy(_R__UNIQUE_DICT_(Init));

   // Dictionary for non-ClassDef classes
   static TClass *RooPowerLawSum_Dictionary() {
      TClass* theClass =::ROOT::GenerateInitInstanceLocal((const ::RooPowerLawSum*)0x0)->GetClass();
      RooPowerLawSum_TClassManip(theClass);
   return theClass;
   }

   static void RooPowerLawSum_TClassManip(TClass* ){
   }

} // end of namespace ROOT

namespace ROOT {
   static TClass *WSTFileWrapper_Dictionary();
   static void WSTFileWrapper_TClassManip(TClass*);
   static void delete_WSTFileWrapper(void *p);
   static void deleteArray_WSTFileWrapper(void *p);
   static void destruct_WSTFileWrapper(void *p);

   // Function generating the singleton type initializer
   static TGenericClassInfo *GenerateInitInstanceLocal(const ::WSTFileWrapper*)
   {
      ::WSTFileWrapper *ptr = 0;
      static ::TVirtualIsAProxy* isa_proxy = new ::TIsAProxy(typeid(::WSTFileWrapper));
      static ::ROOT::TGenericClassInfo 
         instance("WSTFileWrapper", "interface/WSTFileWrapper.h", 10,
                  typeid(::WSTFileWrapper), ::ROOT::Internal::DefineBehavior(ptr, ptr),
                  &WSTFileWrapper_Dictionary, isa_proxy, 0,
                  sizeof(::WSTFileWrapper) );
      instance.SetDelete(&delete_WSTFileWrapper);
      instance.SetDeleteArray(&deleteArray_WSTFileWrapper);
      instance.SetDestructor(&destruct_WSTFileWrapper);
      return &instance;
   }
   TGenericClassInfo *GenerateInitInstance(const ::WSTFileWrapper*)
   {
      return GenerateInitInstanceLocal((::WSTFileWrapper*)0);
   }
   // Static variable to force the class initialization
   static ::ROOT::TGenericClassInfo *_R__UNIQUE_DICT_(Init) = GenerateInitInstanceLocal((const ::WSTFileWrapper*)0x0); R__UseDummy(_R__UNIQUE_DICT_(Init));

   // Dictionary for non-ClassDef classes
   static TClass *WSTFileWrapper_Dictionary() {
      TClass* theClass =::ROOT::GenerateInitInstanceLocal((const ::WSTFileWrapper*)0x0)->GetClass();
      WSTFileWrapper_TClassManip(theClass);
   return theClass;
   }

   static void WSTFileWrapper_TClassManip(TClass* ){
   }

} // end of namespace ROOT

namespace ROOT {
   static TClass *RooExponentialSum_Dictionary();
   static void RooExponentialSum_TClassManip(TClass*);
   static void *new_RooExponentialSum(void *p = 0);
   static void *newArray_RooExponentialSum(Long_t size, void *p);
   static void delete_RooExponentialSum(void *p);
   static void deleteArray_RooExponentialSum(void *p);
   static void destruct_RooExponentialSum(void *p);

   // Function generating the singleton type initializer
   static TGenericClassInfo *GenerateInitInstanceLocal(const ::RooExponentialSum*)
   {
      ::RooExponentialSum *ptr = 0;
      static ::TVirtualIsAProxy* isa_proxy = new ::TIsAProxy(typeid(::RooExponentialSum));
      static ::ROOT::TGenericClassInfo 
         instance("RooExponentialSum", "interface/RooExponentialSum.h", 26,
                  typeid(::RooExponentialSum), ::ROOT::Internal::DefineBehavior(ptr, ptr),
                  &RooExponentialSum_Dictionary, isa_proxy, 0,
                  sizeof(::RooExponentialSum) );
      instance.SetNew(&new_RooExponentialSum);
      instance.SetNewArray(&newArray_RooExponentialSum);
      instance.SetDelete(&delete_RooExponentialSum);
      instance.SetDeleteArray(&deleteArray_RooExponentialSum);
      instance.SetDestructor(&destruct_RooExponentialSum);
      return &instance;
   }
   TGenericClassInfo *GenerateInitInstance(const ::RooExponentialSum*)
   {
      return GenerateInitInstanceLocal((::RooExponentialSum*)0);
   }
   // Static variable to force the class initialization
   static ::ROOT::TGenericClassInfo *_R__UNIQUE_DICT_(Init) = GenerateInitInstanceLocal((const ::RooExponentialSum*)0x0); R__UseDummy(_R__UNIQUE_DICT_(Init));

   // Dictionary for non-ClassDef classes
   static TClass *RooExponentialSum_Dictionary() {
      TClass* theClass =::ROOT::GenerateInitInstanceLocal((const ::RooExponentialSum*)0x0)->GetClass();
      RooExponentialSum_TClassManip(theClass);
   return theClass;
   }

   static void RooExponentialSum_TClassManip(TClass* ){
   }

} // end of namespace ROOT

namespace ROOT {
   static TClass *RooPowerLaw_Dictionary();
   static void RooPowerLaw_TClassManip(TClass*);
   static void *new_RooPowerLaw(void *p = 0);
   static void *newArray_RooPowerLaw(Long_t size, void *p);
   static void delete_RooPowerLaw(void *p);
   static void deleteArray_RooPowerLaw(void *p);
   static void destruct_RooPowerLaw(void *p);

   // Function generating the singleton type initializer
   static TGenericClassInfo *GenerateInitInstanceLocal(const ::RooPowerLaw*)
   {
      ::RooPowerLaw *ptr = 0;
      static ::TVirtualIsAProxy* isa_proxy = new ::TIsAProxy(typeid(::RooPowerLaw));
      static ::ROOT::TGenericClassInfo 
         instance("RooPowerLaw", "interface/RooPowerLaw.h", 25,
                  typeid(::RooPowerLaw), ::ROOT::Internal::DefineBehavior(ptr, ptr),
                  &RooPowerLaw_Dictionary, isa_proxy, 0,
                  sizeof(::RooPowerLaw) );
      instance.SetNew(&new_RooPowerLaw);
      instance.SetNewArray(&newArray_RooPowerLaw);
      instance.SetDelete(&delete_RooPowerLaw);
      instance.SetDeleteArray(&deleteArray_RooPowerLaw);
      instance.SetDestructor(&destruct_RooPowerLaw);
      return &instance;
   }
   TGenericClassInfo *GenerateInitInstance(const ::RooPowerLaw*)
   {
      return GenerateInitInstanceLocal((::RooPowerLaw*)0);
   }
   // Static variable to force the class initialization
   static ::ROOT::TGenericClassInfo *_R__UNIQUE_DICT_(Init) = GenerateInitInstanceLocal((const ::RooPowerLaw*)0x0); R__UseDummy(_R__UNIQUE_DICT_(Init));

   // Dictionary for non-ClassDef classes
   static TClass *RooPowerLaw_Dictionary() {
      TClass* theClass =::ROOT::GenerateInitInstanceLocal((const ::RooPowerLaw*)0x0)->GetClass();
      RooPowerLaw_TClassManip(theClass);
   return theClass;
   }

   static void RooPowerLaw_TClassManip(TClass* ){
   }

} // end of namespace ROOT

namespace ROOT {
   static TClass *ProfileMultiplePdfs_Dictionary();
   static void ProfileMultiplePdfs_TClassManip(TClass*);
   static void *new_ProfileMultiplePdfs(void *p = 0);
   static void *newArray_ProfileMultiplePdfs(Long_t size, void *p);
   static void delete_ProfileMultiplePdfs(void *p);
   static void deleteArray_ProfileMultiplePdfs(void *p);
   static void destruct_ProfileMultiplePdfs(void *p);

   // Function generating the singleton type initializer
   static TGenericClassInfo *GenerateInitInstanceLocal(const ::ProfileMultiplePdfs*)
   {
      ::ProfileMultiplePdfs *ptr = 0;
      static ::TVirtualIsAProxy* isa_proxy = new ::TIsAProxy(typeid(::ProfileMultiplePdfs));
      static ::ROOT::TGenericClassInfo 
         instance("ProfileMultiplePdfs", "interface/ProfileMultiplePdfs.h", 18,
                  typeid(::ProfileMultiplePdfs), ::ROOT::Internal::DefineBehavior(ptr, ptr),
                  &ProfileMultiplePdfs_Dictionary, isa_proxy, 0,
                  sizeof(::ProfileMultiplePdfs) );
      instance.SetNew(&new_ProfileMultiplePdfs);
      instance.SetNewArray(&newArray_ProfileMultiplePdfs);
      instance.SetDelete(&delete_ProfileMultiplePdfs);
      instance.SetDeleteArray(&deleteArray_ProfileMultiplePdfs);
      instance.SetDestructor(&destruct_ProfileMultiplePdfs);
      return &instance;
   }
   TGenericClassInfo *GenerateInitInstance(const ::ProfileMultiplePdfs*)
   {
      return GenerateInitInstanceLocal((::ProfileMultiplePdfs*)0);
   }
   // Static variable to force the class initialization
   static ::ROOT::TGenericClassInfo *_R__UNIQUE_DICT_(Init) = GenerateInitInstanceLocal((const ::ProfileMultiplePdfs*)0x0); R__UseDummy(_R__UNIQUE_DICT_(Init));

   // Dictionary for non-ClassDef classes
   static TClass *ProfileMultiplePdfs_Dictionary() {
      TClass* theClass =::ROOT::GenerateInitInstanceLocal((const ::ProfileMultiplePdfs*)0x0)->GetClass();
      ProfileMultiplePdfs_TClassManip(theClass);
   return theClass;
   }

   static void ProfileMultiplePdfs_TClassManip(TClass* ){
   }

} // end of namespace ROOT

namespace ROOT {
   static TClass *PdfModelBuilder_Dictionary();
   static void PdfModelBuilder_TClassManip(TClass*);
   static void *new_PdfModelBuilder(void *p = 0);
   static void *newArray_PdfModelBuilder(Long_t size, void *p);
   static void delete_PdfModelBuilder(void *p);
   static void deleteArray_PdfModelBuilder(void *p);
   static void destruct_PdfModelBuilder(void *p);

   // Function generating the singleton type initializer
   static TGenericClassInfo *GenerateInitInstanceLocal(const ::PdfModelBuilder*)
   {
      ::PdfModelBuilder *ptr = 0;
      static ::TVirtualIsAProxy* isa_proxy = new ::TIsAProxy(typeid(::PdfModelBuilder));
      static ::ROOT::TGenericClassInfo 
         instance("PdfModelBuilder", "interface/PdfModelBuilder.h", 21,
                  typeid(::PdfModelBuilder), ::ROOT::Internal::DefineBehavior(ptr, ptr),
                  &PdfModelBuilder_Dictionary, isa_proxy, 0,
                  sizeof(::PdfModelBuilder) );
      instance.SetNew(&new_PdfModelBuilder);
      instance.SetNewArray(&newArray_PdfModelBuilder);
      instance.SetDelete(&delete_PdfModelBuilder);
      instance.SetDeleteArray(&deleteArray_PdfModelBuilder);
      instance.SetDestructor(&destruct_PdfModelBuilder);
      return &instance;
   }
   TGenericClassInfo *GenerateInitInstance(const ::PdfModelBuilder*)
   {
      return GenerateInitInstanceLocal((::PdfModelBuilder*)0);
   }
   // Static variable to force the class initialization
   static ::ROOT::TGenericClassInfo *_R__UNIQUE_DICT_(Init) = GenerateInitInstanceLocal((const ::PdfModelBuilder*)0x0); R__UseDummy(_R__UNIQUE_DICT_(Init));

   // Dictionary for non-ClassDef classes
   static TClass *PdfModelBuilder_Dictionary() {
      TClass* theClass =::ROOT::GenerateInitInstanceLocal((const ::PdfModelBuilder*)0x0)->GetClass();
      PdfModelBuilder_TClassManip(theClass);
   return theClass;
   }

   static void PdfModelBuilder_TClassManip(TClass* ){
   }

} // end of namespace ROOT

namespace ROOT {
   // Wrappers around operator new
   static void *new_RooPowerLawSum(void *p) {
      return  p ? new(p) ::RooPowerLawSum : new ::RooPowerLawSum;
   }
   static void *newArray_RooPowerLawSum(Long_t nElements, void *p) {
      return p ? new(p) ::RooPowerLawSum[nElements] : new ::RooPowerLawSum[nElements];
   }
   // Wrapper around operator delete
   static void delete_RooPowerLawSum(void *p) {
      delete ((::RooPowerLawSum*)p);
   }
   static void deleteArray_RooPowerLawSum(void *p) {
      delete [] ((::RooPowerLawSum*)p);
   }
   static void destruct_RooPowerLawSum(void *p) {
      typedef ::RooPowerLawSum current_t;
      ((current_t*)p)->~current_t();
   }
} // end of namespace ROOT for class ::RooPowerLawSum

namespace ROOT {
   // Wrapper around operator delete
   static void delete_WSTFileWrapper(void *p) {
      delete ((::WSTFileWrapper*)p);
   }
   static void deleteArray_WSTFileWrapper(void *p) {
      delete [] ((::WSTFileWrapper*)p);
   }
   static void destruct_WSTFileWrapper(void *p) {
      typedef ::WSTFileWrapper current_t;
      ((current_t*)p)->~current_t();
   }
} // end of namespace ROOT for class ::WSTFileWrapper

namespace ROOT {
   // Wrappers around operator new
   static void *new_RooExponentialSum(void *p) {
      return  p ? new(p) ::RooExponentialSum : new ::RooExponentialSum;
   }
   static void *newArray_RooExponentialSum(Long_t nElements, void *p) {
      return p ? new(p) ::RooExponentialSum[nElements] : new ::RooExponentialSum[nElements];
   }
   // Wrapper around operator delete
   static void delete_RooExponentialSum(void *p) {
      delete ((::RooExponentialSum*)p);
   }
   static void deleteArray_RooExponentialSum(void *p) {
      delete [] ((::RooExponentialSum*)p);
   }
   static void destruct_RooExponentialSum(void *p) {
      typedef ::RooExponentialSum current_t;
      ((current_t*)p)->~current_t();
   }
} // end of namespace ROOT for class ::RooExponentialSum

namespace ROOT {
   // Wrappers around operator new
   static void *new_RooPowerLaw(void *p) {
      return  p ? new(p) ::RooPowerLaw : new ::RooPowerLaw;
   }
   static void *newArray_RooPowerLaw(Long_t nElements, void *p) {
      return p ? new(p) ::RooPowerLaw[nElements] : new ::RooPowerLaw[nElements];
   }
   // Wrapper around operator delete
   static void delete_RooPowerLaw(void *p) {
      delete ((::RooPowerLaw*)p);
   }
   static void deleteArray_RooPowerLaw(void *p) {
      delete [] ((::RooPowerLaw*)p);
   }
   static void destruct_RooPowerLaw(void *p) {
      typedef ::RooPowerLaw current_t;
      ((current_t*)p)->~current_t();
   }
} // end of namespace ROOT for class ::RooPowerLaw

namespace ROOT {
   // Wrappers around operator new
   static void *new_ProfileMultiplePdfs(void *p) {
      return  p ? new(p) ::ProfileMultiplePdfs : new ::ProfileMultiplePdfs;
   }
   static void *newArray_ProfileMultiplePdfs(Long_t nElements, void *p) {
      return p ? new(p) ::ProfileMultiplePdfs[nElements] : new ::ProfileMultiplePdfs[nElements];
   }
   // Wrapper around operator delete
   static void delete_ProfileMultiplePdfs(void *p) {
      delete ((::ProfileMultiplePdfs*)p);
   }
   static void deleteArray_ProfileMultiplePdfs(void *p) {
      delete [] ((::ProfileMultiplePdfs*)p);
   }
   static void destruct_ProfileMultiplePdfs(void *p) {
      typedef ::ProfileMultiplePdfs current_t;
      ((current_t*)p)->~current_t();
   }
} // end of namespace ROOT for class ::ProfileMultiplePdfs

namespace ROOT {
   // Wrappers around operator new
   static void *new_PdfModelBuilder(void *p) {
      return  p ? new(p) ::PdfModelBuilder : new ::PdfModelBuilder;
   }
   static void *newArray_PdfModelBuilder(Long_t nElements, void *p) {
      return p ? new(p) ::PdfModelBuilder[nElements] : new ::PdfModelBuilder[nElements];
   }
   // Wrapper around operator delete
   static void delete_PdfModelBuilder(void *p) {
      delete ((::PdfModelBuilder*)p);
   }
   static void deleteArray_PdfModelBuilder(void *p) {
      delete [] ((::PdfModelBuilder*)p);
   }
   static void destruct_PdfModelBuilder(void *p) {
      typedef ::PdfModelBuilder current_t;
      ((current_t*)p)->~current_t();
   }
} // end of namespace ROOT for class ::PdfModelBuilder

namespace {
  void TriggerDictionaryInitialization_RootDict_Impl() {
    static const char* headers[] = {
"interface/RooPowerLawSum.h",
"interface/WSTFileWrapper.h",
"interface/RooExponentialSum.h",
"interface/RooPowerLaw.h",
"interface/ProfileMultiplePdfs.h",
"interface/PdfModelBuilder.h",
0
    };
    static const char* includePaths[] = {
"/cvmfs/cms.cern.ch/slc7_amd64_gcc700/lcg/root/6.12.07-gnimlf5//include",
"/cvmfs/cms.cern.ch/slc7_amd64_gcc700/lcg/root/6.12.07-gnimlf5/include",
"/home/users/yagu/XYH/FinalFit/CMSSW_10_2_13/src/flashggFinalFit/Background/",
0
    };
    static const char* fwdDeclCode = R"DICTFWDDCLS(
#line 1 "RootDict dictionary forward declarations' payload"
#pragma clang diagnostic ignored "-Wkeyword-compat"
#pragma clang diagnostic ignored "-Wignored-attributes"
#pragma clang diagnostic ignored "-Wreturn-type-c-linkage"
extern int __Cling_Autoloading_Map;
class __attribute__((annotate("$clingAutoload$interface/RooPowerLawSum.h")))  RooPowerLawSum;
class __attribute__((annotate("$clingAutoload$interface/WSTFileWrapper.h")))  WSTFileWrapper;
class __attribute__((annotate("$clingAutoload$interface/RooExponentialSum.h")))  RooExponentialSum;
class __attribute__((annotate("$clingAutoload$interface/RooPowerLaw.h")))  RooPowerLaw;
class __attribute__((annotate("$clingAutoload$interface/ProfileMultiplePdfs.h")))  ProfileMultiplePdfs;
class __attribute__((annotate("$clingAutoload$interface/PdfModelBuilder.h")))  PdfModelBuilder;
)DICTFWDDCLS";
    static const char* payloadCode = R"DICTPAYLOAD(
#line 1 "RootDict dictionary payload"

#ifndef G__VECTOR_HAS_CLASS_ITERATOR
  #define G__VECTOR_HAS_CLASS_ITERATOR 1
#endif

#define _BACKWARD_BACKWARD_WARNING_H
#include "interface/RooPowerLawSum.h"
#include "interface/WSTFileWrapper.h"
#include "interface/RooExponentialSum.h"
#include "interface/RooPowerLaw.h"
#include "interface/ProfileMultiplePdfs.h"
#include "interface/PdfModelBuilder.h"

#undef  _BACKWARD_BACKWARD_WARNING_H
)DICTPAYLOAD";
    static const char* classesHeaders[]={
"PdfModelBuilder", payloadCode, "@",
"ProfileMultiplePdfs", payloadCode, "@",
"RooExponentialSum", payloadCode, "@",
"RooPowerLaw", payloadCode, "@",
"RooPowerLawSum", payloadCode, "@",
"WSTFileWrapper", payloadCode, "@",
nullptr};

    static bool isInitialized = false;
    if (!isInitialized) {
      TROOT::RegisterModule("RootDict",
        headers, includePaths, payloadCode, fwdDeclCode,
        TriggerDictionaryInitialization_RootDict_Impl, {}, classesHeaders);
      isInitialized = true;
    }
  }
  static struct DictInit {
    DictInit() {
      TriggerDictionaryInitialization_RootDict_Impl();
    }
  } __TheDictionaryInitializer;
}
void TriggerDictionaryInitialization_RootDict() {
  TriggerDictionaryInitialization_RootDict_Impl();
}
