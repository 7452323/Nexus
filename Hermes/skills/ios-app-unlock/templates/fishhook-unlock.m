/**
 * iOS App Subscription Unlock Dylib Template
 * 
 * Usage: Modify the HOOK_SYMBOLS array for your target app, then compile:
 *   SDK=$(xcrun --sdk iphoneos --show-sdk-path)
 *   clang -target arm64-apple-ios15.0 -isysroot "$SDK" -fobjc-arc -O2 \
 *       -c fishhook.c -o fishhook.o
 *   clang -target arm64-apple-ios15.0 -isysroot "$SDK" -fobjc-arc -O2 \
 *       -c Unlock.m -o Unlock.o
 *   clang -target arm64-apple-ios15.0 -isysroot "$SDK" -dynamiclib \
 *       -framework Foundation -lobjc \
 *       -install_name "/usr/lib/Unlock.dylib" \
 *       -o Unlock.dylib fishhook.o Unlock.o
 *   ldid -S Unlock.dylib
 *
 * Inject via TrollStore/TrollTools.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <objc/runtime.h>
#include <objc/message.h>
#include <dlfcn.h>
#include "fishhook.h"

// ============================================================
// Hook definitions — MODIFY THESE FOR YOUR TARGET APP
// ============================================================

// Hook 1: RenewalState.rawValue -> always return 1 (subscribed)
// Symbol: _$s8StoreKit7ProductV16SubscriptionInfoV12RenewalStateV8rawValueSivg
static int64_t (*orig_rawValue)(void *self);
static int64_t hooked_rawValue(void *self) { return 1; }

// Hook 2: willAutoRenew -> always return true
// Symbol: _$s8StoreKit7ProductV16SubscriptionInfoV07RenewalE0V13willAutoRenewSbvg
static bool (*orig_willAutoRenew)(void *self);
static bool hooked_willAutoRenew(void *self) { return true; }

// Hook 3: Status.state -> always return subscribed
// Symbol: _$s8StoreKit7ProductV16SubscriptionInfoV6StatusV5stateAE12RenewalStateVvg
static void (*orig_statusState)(void *self, void *result);
static void hooked_statusState(void *self, void *result) {
    if (orig_statusState) orig_statusState(self, result);
    int64_t *raw = (int64_t *)result;
    *raw = 1; // subscribed
}

// ============================================================
// Rebinding table
// ============================================================
static struct rebinding g_rebindings[] = {
    {"_$s8StoreKit7ProductV16SubscriptionInfoV12RenewalStateV8rawValueSivg",
     (void *)hooked_rawValue, (void **)&orig_rawValue},
    {"_$s8StoreKit7ProductV16SubscriptionInfoV07RenewalE0V13willAutoRenewSbvg",
     (void *)hooked_willAutoRenew, (void **)&orig_willAutoRenew},
    {"_$s8StoreKit7ProductV16SubscriptionInfoV6StatusV5stateAE12RenewalStateVvg",
     (void *)hooked_statusState, (void **)&orig_statusState},
};

// ============================================================
// NSUserDefaults force-set (optional, belt-and-suspenders)
// ============================================================
static void forceDefaults(void) {
    id defaults = ((id (*)(id, SEL))objc_msgSend)(
        objc_getClass("NSUserDefaults"),
        sel_registerName("standardUserDefaults"));
    if (!defaults) return;

    SEL setBool = sel_registerName("setBool:forKey:");
    SEL setInt  = sel_registerName("setInteger:forKey:");
    SEL sync    = sel_registerName("synchronize");

    id (*str)(id, SEL, const char *) = (id (*)(id, SEL, const char *))objc_msgSend;

    ((void (*)(id, SEL, BOOL, id))objc_msgSend)(defaults, setBool, YES,
        str(objc_getClass("NSString"), sel_registerName("stringWithUTF8String:"),
            "subscriptionWillAutoRenew"));
    ((void (*)(id, SEL, BOOL, id))objc_msgSend)(defaults, setBool, NO,
        str(objc_getClass("NSString"), sel_registerName("stringWithUTF8String:"),
            "subscriptionWasRefunded"));
    ((void (*)(id, SEL, int64_t, id))objc_msgSend)(defaults, setInt, 1,
        str(objc_getClass("NSString"), sel_registerName("stringWithUTF8String:"),
            "subscriptionStateRawValue"));
    ((void (*)(id, SEL))objc_msgSend)(defaults, sync);
}

// ============================================================
// Sentry disable (optional)
// ============================================================
static void disableSentry(void) {
    Class cls = objc_getClass("SentrySDK");
    if (!cls) return;
    Method m = class_getClassMethod(cls, sel_registerName("startWithOptions:"));
    if (!m) return;
    IMP noop = imp_implementationWithBlock(^(id s, id o) {});
    method_setImplementation(m, noop);
}

// ============================================================
// Constructor
// ============================================================
__attribute__((constructor))
static void UnlockInit(void) {
    rebind_symbols(g_rebindings,
                   sizeof(g_rebindings) / sizeof(g_rebindings[0]));
    forceDefaults();
    disableSentry();
}
