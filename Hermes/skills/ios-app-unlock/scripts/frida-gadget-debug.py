#!/usr/bin/env python3
"""
Frida Gadget Debug Script — Attach to iOS app via USB with Frida Gadget injected.

Usage:
  1. Inject FridaGadget.dylib into target app (via TrollTools or IPA repack)
  2. USB connect iPad to Mac
  3. Launch the target app on iPad
  4. Run this script: python3 frida-gadget-debug.py [--js debug.js] [--process Gadget]

Requirements:
  pip3 install frida frida-tools

Notes:
  - frida CLI has asyncio bugs in non-interactive environments; use Python API instead
  - Non-jailbreak devices MUST use Frida Gadget (not frida-server)
  - TrollStore can inject Gadget via TrollTools directly (no IPA repack needed)
"""

import frida
import sys
import time
import argparse
import os

def find_js_script(name):
    """Search for JS script in common locations."""
    search_paths = [
        name,  # absolute/relative path as-is
        os.path.join(os.path.dirname(__file__), name),
        os.path.join(os.path.expanduser("~"), "Downloads", name),
        os.path.join("/tmp", name),
    ]
    for p in search_paths:
        if os.path.isfile(p):
            return p
    return None

def main():
    parser = argparse.ArgumentParser(description="Frida Gadget Debug Attacher")
    parser.add_argument("--js", default=None, help="Path to JavaScript debug script")
    parser.add_argument("--process", default="Gadget", help="Process name (default: Gadget)")
    parser.add_argument("--timeout", type=int, default=10, help="USB device timeout in seconds")
    parser.add_argument("--list", action="store_true", help="List running processes and exit")
    args = parser.parse_args()

    # Connect to USB device
    try:
        device = frida.get_usb_device(timeout=args.timeout)
        print(f"[*] Device: {device.name} ({device.id})")
    except frida.ServerNotRunningError:
        print("[!] Frida server not running on device. Is Gadget injected?")
        sys.exit(1)
    except frida.TransportError as e:
        print(f"[!] Cannot connect to device: {e}")
        print("[!] Make sure: (1) iPad is USB-connected (2) App is running (3) Gadget is injected")
        sys.exit(1)

    if args.list:
        print("[*] Running processes:")
        for proc in device.enumerate_processes():
            print(f"  PID={proc.pid:6d}  {proc.name}")
        return

    # Find JS script
    js_code = ""
    if args.js:
        js_path = find_js_script(args.js)
        if js_path:
            with open(js_path) as f:
                js_code = f.read()
            print(f"[*] Loaded script: {js_path} ({len(js_code)} bytes)")
        else:
            print(f"[!] Script not found: {args.js}")
            sys.exit(1)
    else:
        # Default inline script — explore ObjC classes and ivars
        js_code = r"""
        'use strict';

        if (ObjC.available) {
            console.log("[*] ObjC runtime available");

            // List all classes containing 'SubsStore' or 'Subscription'
            var classes = ObjC.classes;
            var storeClasses = [];
            for (var name in classes) {
                if (name.indexOf("SubsStore") !== -1 || name.indexOf("Subscription") !== -1) {
                    storeClasses.push(name);
                }
            }
            console.log("[*] Subscription-related classes: " + JSON.stringify(storeClasses));

            // For each found class, dump ivars
            storeClasses.forEach(function(className) {
                try {
                    var cls = ObjC.classes[className];
                    if (cls && cls.$ivars) {
                        console.log("[*] " + className + " ivars: " + JSON.stringify(cls.$ivars));
                    }
                } catch(e) {}
            });

            // Hook alloc for store classes to capture instances
            storeClasses.forEach(function(className) {
                try {
                    var cls = ObjC.classes[className];
                    if (cls) {
                        Interceptor.attach(cls["- alloc"].implementation, {
                            onLeave: function(retval) {
                                send({type: "alloc", class: className, ptr: retval.toString()});
                            }
                        });
                        console.log("[*] Hooked -[" + className + " alloc]");
                    }
                } catch(e) {
                    console.log("[!] Cannot hook " + className + ": " + e);
                }
            });

        } else {
            console.log("[!] ObjC runtime not available");
        }
        """
        print("[*] Using default exploration script")

    # Attach to process
    try:
        session = device.attach(args.process)
        print(f"[*] Attached to process: {args.process} (PID={session._impl})")
    except frida.ProcessNotFoundError:
        print(f"[!] Process '{args.process}' not found.")
        print("[*] Listing running processes:")
        for proc in device.enumerate_processes():
            print(f"  PID={proc.pid:6d}  {proc.name}")
        sys.exit(1)

    script = session.create_script(js_code)

    def on_message(message, data):
        if message["type"] == "send":
            payload = message["payload"]
            if isinstance(payload, dict):
                if payload.get("type") == "alloc":
                    print(f"[ALLOC] {payload['class']}: {payload['ptr']}")
                else:
                    print(f"[MSG] {payload}")
            else:
                print(f"[MSG] {payload}")
        elif message["type"] == "error":
            print(f"[ERR] {message['description']}")
        else:
            print(f"[{message['type']}] {message}")

    script.on("message", on_message)
    script.load()
    print("[*] Script loaded. Press Ctrl+C to detach.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[*] Detaching...")
        session.detach()
        print("[*] Done.")

if __name__ == "__main__":
    main()
