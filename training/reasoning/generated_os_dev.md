# Generated OS Development Training — Iris AI
# Teaches Iris to create operating systems from scratch

USER: Create a complete multiboot bootloader in NASM assembly for a 32-bit x86 kernel. Include the multiboot header with framebuffer request (1024x768x32), a 16KB stack in BSS, and the entry point that calls kernel_main. Use i686-elf cross compiler conventions.
BOT: Here's a complete multiboot bootloader:

```asm
; boot.asm — Multiboot-compliant 32-bit bootloader
; Build with: nasm -f elf32 boot.asm -o boot.o

section .multiboot
align 4
multiboot_header:
    dd 0x1BADB002              ; magic
    dd 0x00000007              ; flags: page-align + mem info + video
    dd -(0x1BADB002 + 0x00000007) ; checksum
    dd multiboot_header        ; header_addr
    dd _start                  ; load_addr
    dd 0                       ; load_end_addr
    dd 0                       ; bss_end_addr
    dd _start                  ; entry_addr
    dd 0                       ; mode_type: 0 = linear graphics
    dd 1024                    ; width
    dd 768                     ; height
    dd 32                      ; depth

section .bss
align 16
stack_bottom:
    resb 16384                 ; 16 KB stack
stack_top:

section .text
global _start
extern kernel_main             ; defined in kernel.c

_start:
    mov esp, stack_top         ; set up stack
    push ebx                   ; push multiboot_info pointer
    push eax                   ; push multiboot magic
    call kernel_main
    cli
.hang:
    hlt
    jmp .hang
```

Key multiboot conventions:
- Magic `0x1BADB002` identifies it as a multiboot kernel
- Bit 2 in flags (`0x04`) requests video mode info — GRUB sets up the framebuffer
- Linear framebuffer mode (mode_type=0) gives a flat pixel buffer via the multiboot info struct
- `_start` is the entry symbol referenced in the linker script
- `ebx` contains the multiboot info pointer, `eax` contains `0x2BADB002` magic

USER: Write a linker script (linker.ld) for a 32-bit x86 kernel built with i686-elf-ld. Place the multiboot header in the .text section at 1MB, then .text, .rodata, .data, .bss aligned at 4K boundaries.
BOT: Here's the linker script:

```ld
/* linker.ld — Linker script for 32-bit x86 kernel */
ENTRY(_start)

SECTIONS
{
    . = 1M;                    /* Load kernel at 1MB */

    .text BLOCK(4K) : ALIGN(4K)
    {
        *(.multiboot)          /* Multiboot header must be first */
        *(.text)
    }

    .rodata BLOCK(4K) : ALIGN(4K)
    {
        *(.rodata)
    }

    .data BLOCK(4K) : ALIGN(4K)
    {
        *(.data)
    }

    .bss BLOCK(4K) : ALIGN(4K)
    {
        *(COMMON)
        *(.bss)
    }

    . = ALIGN(4K);
    __end = .;                 /* End-of-kernel marker */
}
```

Key details:
- `ENTRY(_start)` tells the linker where execution begins
- `. = 1M` loads the kernel above the first 1MB (above BIOS/GRUB reserved area)
- `BLOCK(4K)` and `ALIGN(4K)` align sections for paging (4K page boundaries)
- `.multiboot` is placed first so the multiboot header is at the very start
- `__end` provides an end-of-kernel address for heap or additional memory management

USER: Write a Makefile for building a 32-bit x86 OS kernel using i686-elf-gcc cross-compiler and NASM assembler. Include targets for compiling C and ASM sources, linking kernel.bin, creating an ISO with GRUB, and a run target using QEMU.
BOT: Here's the complete Makefile:

```makefile
# Makefile — Build system for 32-bit x86 OS kernel
ISO_NAME = os.iso
KERNEL_BIN = out/kernel.bin
OUT_DIR = out

BOOT_OBJ = $(OUT_DIR)/boot.o
OBJS = $(OUT_DIR)/kernel.o $(OUT_DIR)/gdt.o $(OUT_DIR)/gdt_flush.o \
       $(OUT_DIR)/idt.o $(OUT_DIR)/idt_flush.o $(OUT_DIR)/isr.o \
       $(OUT_DIR)/isr_handlers.o $(OUT_DIR)/paging.o $(OUT_DIR)/vbe.o \
       $(OUT_DIR)/gui.o $(OUT_DIR)/wm.o $(OUT_DIR)/mouse.o \
       $(OUT_DIR)/keyboard.o $(OUT_DIR)/timer.o $(OUT_DIR)/vfs.o \
       $(OUT_DIR)/string.o $(OUT_DIR)/font8x8.o

CC = i686-elf-gcc
AS = nasm
LD = i686-elf-ld
CFLAGS = -m32 -ffreestanding -fno-exceptions -nostdlib -nostdinc \
         -Wall -Wextra -std=c11 -I src/include
ASFLAGS = -f elf32
LDFLAGS = -m elf_i386 -T linker.ld

all: $(ISO_NAME)

$(ISO_NAME): $(KERNEL_BIN)

$(KERNEL_BIN): $(BOOT_OBJ) $(OBJS)
	$(LD) $(LDFLAGS) -o $@ $(BOOT_OBJ) $(OBJS)

$(OUT_DIR):
	mkdir -p $(OUT_DIR)

# C source pattern rule
$(OUT_DIR)/%.o: src/%.c | $(OUT_DIR)

# Assembly pattern rule
$(OUT_DIR)/%.o: src/%.asm | $(OUT_DIR)
	$(AS) $(ASFLAGS) -o $@ $<

# Individual source rules
$(OUT_DIR)/kernel.o: src/kernel/kernel.c | $(OUT_DIR)
	$(CC) $(CFLAGS) -c -o $@ $<

$(OUT_DIR)/boot.o: src/boot/boot.asm | $(OUT_DIR)
	$(AS) $(ASFLAGS) -o $@ $<

$(OUT_DIR)/gdt.o: src/cpu/gdt.c | $(OUT_DIR)
	$(CC) $(CFLAGS) -c -o $@ $<

$(OUT_DIR)/gdt_flush.o: src/cpu/gdt_flush.asm | $(OUT_DIR)
	$(AS) $(ASFLAGS) -o $@ $<

$(OUT_DIR)/idt.o: src/cpu/idt.c | $(OUT_DIR)
	$(CC) $(CFLAGS) -c -o $@ $<

$(OUT_DIR)/idt_flush.o: src/cpu/idt_flush.asm | $(OUT_DIR)
	$(AS) $(ASFLAGS) -o $@ $<

$(OUT_DIR)/isr.o: src/cpu/isr.c | $(OUT_DIR)
	$(CC) $(CFLAGS) -c -o $@ $<

$(OUT_DIR)/isr_handlers.o: src/cpu/isr_handlers.asm | $(OUT_DIR)
	$(AS) $(ASFLAGS) -o $@ $<

$(OUT_DIR)/paging.o: src/mem/paging.c | $(OUT_DIR)
	$(CC) $(CFLAGS) -c -o $@ $<

$(OUT_DIR)/vbe.o: src/drivers/vbe.c | $(OUT_DIR)
	$(CC) $(CFLAGS) -c -o $@ $<

$(OUT_DIR)/gui.o: src/gui/gui.c | $(OUT_DIR)
	$(CC) $(CFLAGS) -c -o $@ $<

$(OUT_DIR)/wm.o: src/gui/wm.c | $(OUT_DIR)
	$(CC) $(CFLAGS) -c -o $@ $<

$(OUT_DIR)/mouse.o: src/drivers/mouse.c | $(OUT_DIR)
	$(CC) $(CFLAGS) -c -o $@ $<

$(OUT_DIR)/keyboard.o: src/drivers/keyboard.c | $(OUT_DIR)
	$(CC) $(CFLAGS) -c -o $@ $<

$(OUT_DIR)/timer.o: src/drivers/timer.c | $(OUT_DIR)
	$(CC) $(CFLAGS) -c -o $@ $<

$(OUT_DIR)/vfs.o: src/fs/vfs.c | $(OUT_DIR)
	$(CC) $(CFLAGS) -c -o $@ $<

$(OUT_DIR)/string.o: src/lib/string.c | $(OUT_DIR)
	$(CC) $(CFLAGS) -c -o $@ $<

$(OUT_DIR)/font8x8.o: src/lib/font8x8.c | $(OUT_DIR)
	$(CC) $(CFLAGS) -c -o $@ $<

# Create bootable ISO with GRUB
iso: $(KERNEL_BIN)
	mkdir -p iso/boot/grub
	cp $(KERNEL_BIN) iso/boot/
	echo 'set timeout=0' > iso/boot/grub/grub.cfg
	echo 'set default=0' >> iso/boot/grub/grub.cfg
	echo 'menuentry "MyOS" {' >> iso/boot/grub/grub.cfg
	echo '    set gfxpayload=1024x768x32' >> iso/boot/grub/grub.cfg
	echo '    multiboot /boot/kernel.bin' >> iso/boot/grub/grub.cfg
	echo '}' >> iso/boot/grub/grub.cfg
	grub-mkrescue -o $(ISO_NAME) iso 2>/dev/null

# Run in QEMU
run: iso
	qemu-system-i386 -cdrom $(ISO_NAME) -m 128

clean:
	rm -rf $(OUT_DIR) $(ISO_NAME) iso

.PHONY: all iso run clean
```

Critical compiler flags for kernel development:
- `-ffreestanding`: tells GCC not to assume standard library functions exist
- `-nostdlib -nostdinc`: no standard library or includes
- `-fno-exceptions`: disables C++ exception support (saves size)
- `-m32`: compile for 32-bit protected mode
- `-std=c11`: use C11 standard (clean, modern, well-supported for kernels)

USER: Write the core types header (types.h) for a 32-bit OS kernel. Define uint8_t through uint64_t, size_t, and NULL.
BOT: ```c
#ifndef TYPES_H
#define TYPES_H

typedef unsigned char      uint8_t;
typedef unsigned short     uint16_t;
typedef unsigned int       uint32_t;
typedef unsigned long long uint64_t;

typedef signed char        int8_t;
typedef signed short       int16_t;
typedef signed int         int32_t;
typedef signed long long   int64_t;

typedef uint32_t size_t;

#define NULL ((void*)0)

#endif
```

The typedefs use the natural sizes for 32-bit x86: `int` = 32 bits, `short` = 16 bits, `long long` = 64 bits. `size_t` is `uint32_t` because the kernel runs in 32-bit mode with a 32-bit address space.

USER: Write the I/O ports header (ports.h) with inline assembly functions for port I/O: outb, inb, outw, inw, outl, inl, and io_wait. Use GCC inline assembly syntax.
BOT: ```c
#ifndef PORTS_H
#define PORTS_H

#include "types.h"

static inline void outb(uint16_t port, uint8_t val) {
    __asm__ volatile ("outb %0, %1" : : "a"(val), "Nd"(port));
}

static inline uint8_t inb(uint16_t port) {
    uint8_t ret;
    __asm__ volatile ("inb %1, %0" : "=a"(ret) : "Nd"(port));
    return ret;
}

static inline void outw(uint16_t port, uint16_t val) {
    __asm__ volatile ("outw %0, %1" : : "a"(val), "Nd"(port));
}

static inline uint16_t inw(uint16_t port) {
    uint16_t ret;
    __asm__ volatile ("inw %1, %0" : "=a"(ret) : "Nd"(port));
    return ret;
}

static inline void outl(uint16_t port, uint32_t val) {
    __asm__ volatile ("outl %0, %1" : : "a"(val), "Nd"(port));
}

static inline uint32_t inl(uint16_t port) {
    uint32_t ret;
    __asm__ volatile ("inl %1, %0" : "=a"(ret) : "Nd"(port));
    return ret;
}

static inline void io_wait(void) {
    outb(0x80, 0);  /* write to unused port 0x80 for short delay */
}

#endif
```

Key GCC inline assembly conventions:
- `"a"` constraint puts the value in EAX (required by `outb`/`inb`)
- `"Nd"` constraint allows immediate values 0-255 or EDX for the port
- `volatile` prevents GCC from optimizing away I/O instructions
- `outb 0x80, 0` is the classic I/O delay — writes to an unused diagnostic port

USER: Write the multiboot info header (multiboot.h) that parses the structure passed by GRUB. Include fields for framebuffer address, pitch, width, height, BPP, VBE mode info, memory map, and command line.
BOT: ```c
#ifndef MULTIBOOT_H
#define MULTIBOOT_H

#include "types.h"

#define MULTIBOOT_MAGIC         0x1BADB002
#define MULTIBOOT_EAX_MAGIC     0x2BADB002
#define MULTIBOOT_FLAG_MEM      (1 << 0)
#define MULTIBOOT_FLAG_CMDLINE  (1 << 2)
#define MULTIBOOT_FLAG_MODS     (1 << 3)
#define MULTIBOOT_FLAG_MMAP     (1 << 6)
#define MULTIBOOT_FLAG_VBE      (1 << 11)
#define MULTIBOOT_FLAG_FB       (1 << 12)

typedef struct multiboot_info {
    uint32_t flags;              /* bitmask of available fields */

    /* Memory (if flags[0]) */
    uint32_t mem_lower;          /* KB of lower memory (< 1MB) */
    uint32_t mem_upper;          /* KB of upper memory (>= 1MB) */

    uint32_t boot_device;
    uint32_t cmdline;            /* pointer to kernel command line */
    uint32_t mods_count;         /* number of loaded modules */
    uint32_t mods_addr;          /* pointer to module structures */

    /* ELF section header info */
    uint32_t num;
    uint32_t size;
    uint32_t addr;
    uint32_t shndx;

    /* Memory map (if flags[6]) */
    uint32_t mmap_length;
    uint32_t mmap_addr;

    uint32_t drives_length;
    uint32_t drives_addr;
    uint32_t config_table;
    uint32_t boot_loader_name;
    uint32_t apm_table;

    /* VBE (if flags[11]) */
    uint32_t vbe_control_info;
    uint32_t vbe_mode_info;
    uint16_t vbe_mode;
    uint16_t vbe_interface_seg;
    uint16_t vbe_interface_off;
    uint16_t vbe_interface_len;

    /* Framebuffer (if flags[12]) */
    uint64_t framebuffer_addr;   /* physical address of framebuffer */
    uint32_t framebuffer_pitch;  /* bytes per scanline */
    uint32_t framebuffer_width;
    uint32_t framebuffer_height;
    uint8_t  framebuffer_bpp;    /* bits per pixel */
    uint8_t  framebuffer_type;   /* 0=indexed, 1=RGB, 2=EGA text */
    uint8_t  color_info[6];
} __attribute__((packed)) multiboot_info_t;

#endif
```

The `framebuffer_addr` field is how you get direct pixel access — write to that memory address and pixels appear on screen. For 32-bit BPP, each pixel is a 32-bit value (0x00RRGGBB). The `pitch` is the number of bytes per row (usually width × 4 for 32bpp, but may include padding).

USER: Write the GDT (Global Descriptor Table) header and implementation for a 32-bit OS. Define GDT entry struct, GDT pointer struct, gdt_set_gate helper, and gdt_init that sets up null, kernel code, kernel data, user code, and user data segments.
BOT: ```c
// gdt.h
#ifndef GDT_H
#define GDT_H

#include "types.h"

typedef struct gdt_entry {
    uint16_t limit_low;
    uint16_t base_low;
    uint8_t  base_middle;
    uint8_t  access;
    uint8_t  granularity;
    uint8_t  base_high;
} __attribute__((packed)) gdt_entry_t;

typedef struct gdt_ptr {
    uint16_t limit;
    uint32_t base;
} __attribute__((packed)) gdt_ptr_t;

void gdt_init(void);

#endif
```

```c
// gdt.c
#include "gdt.h"
#include "string.h"

static gdt_entry_t gdt_entries[5];
static gdt_ptr_t   gdt_ptr;

extern void gdt_flush(uint32_t gdt_ptr_addr);

static void gdt_set_gate(int32_t num, uint32_t base, uint32_t limit,
                          uint8_t access, uint8_t gran) {
    gdt_entries[num].base_low    = (base & 0xFFFF);
    gdt_entries[num].base_middle = (base >> 16) & 0xFF;
    gdt_entries[num].base_high   = (base >> 24) & 0xFF;
    gdt_entries[num].limit_low   = (limit & 0xFFFF);
    gdt_entries[num].granularity = ((limit >> 16) & 0x0F) | (gran & 0xF0);
    gdt_entries[num].access      = access;
}

void gdt_init(void) {
    gdt_ptr.limit = (sizeof(gdt_entry_t) * 5) - 1;
    gdt_ptr.base  = (uint32_t)&gdt_entries;

    /* Entry 0: Null descriptor (required) */
    gdt_set_gate(0, 0, 0x00000000, 0x00, 0x00);
    /* Entry 1: Kernel code segment — base=0, limit=4GB, DPL=0 */
    gdt_set_gate(1, 0, 0xFFFFFFFF, 0x9A, 0xCF);
    /* Entry 2: Kernel data segment — base=0, limit=4GB, DPL=0 */
    gdt_set_gate(2, 0, 0xFFFFFFFF, 0x92, 0xCF);
    /* Entry 3: User code segment — base=0, limit=4GB, DPL=3 */
    gdt_set_gate(3, 0, 0xFFFFFFFF, 0xFA, 0xCF);
    /* Entry 4: User data segment — base=0, limit=4GB, DPL=3 */
    gdt_set_gate(4, 0, 0xFFFFFFFF, 0xF2, 0xCF);

    gdt_flush((uint32_t)&gdt_ptr);
}
```

```asm
; gdt_flush.asm
global gdt_flush
gdt_flush:
    mov eax, [esp+4]     ; get gdt_ptr address from stack
    lgdt [eax]           ; load GDT register
    
    mov ax, 0x10         ; kernel data segment = 0x10 (entry 2)
    mov ds, ax
    mov es, ax
    mov fs, ax
    mov gs, ax
    mov ss, ax
    
    jmp 0x08:.flush      ; far jump to reload CS with kernel code segment (0x08)
.flush:
    ret
```

Access byte breakdown:
- `0x9A` = `10011010` = present(1) + DPL(00) + code(1) + executable(1) + direction(0) + readable(1) + accessed(0)
- `0x92` = `10010010` = present(1) + DPL(00) + data(0) + direction(0) + writable(1) + accessed(0)
- `0xFA` = `11111010` = present(1) + DPL(11=ring3) + code(1) + executable(1) + ...
- Granularity `0xCF` = `11001111` = 4KB granularity(1) + 32-bit protected mode(1) + limit bits

USER: Write the IDT (Interrupt Descriptor Table) header and implementation. Include idt_set_gate, idt_init, and the assembly flush routine. Use 256-entry IDT, 0x08 code selector, and 0x8E flags (present, DPL=0, 32-bit interrupt gate).
BOT: ```c
// idt.h
#ifndef IDT_H
#define IDT_H

#include "types.h"

typedef struct idt_entry {
    uint16_t base_low;
    uint16_t selector;
    uint8_t  always0;
    uint8_t  flags;
    uint16_t base_high;
} __attribute__((packed)) idt_entry_t;

typedef struct idt_ptr {
    uint16_t limit;
    uint32_t base;
} __attribute__((packed)) idt_ptr_t;

void idt_init(void);
void idt_set_gate(uint8_t num, uint32_t base, uint16_t sel, uint8_t flags);

#endif
```

```c
// idt.c
#include "idt.h"
#include "string.h"

static idt_entry_t idt_entries[256];
static idt_ptr_t   idt_ptr;

extern void idt_flush(uint32_t idt_ptr_addr);

void idt_set_gate(uint8_t num, uint32_t base, uint16_t sel, uint8_t flags) {
    idt_entries[num].base_low  = base & 0xFFFF;
    idt_entries[num].base_high = (base >> 16) & 0xFFFF;
    idt_entries[num].selector  = sel;
    idt_entries[num].always0   = 0;
    idt_entries[num].flags     = flags;
}

void idt_init(void) {
    idt_ptr.limit = (sizeof(idt_entry_t) * 256) - 1;
    idt_ptr.base  = (uint32_t)&idt_entries;
    memset(&idt_entries, 0, sizeof(idt_entries));
    idt_flush((uint32_t)&idt_ptr);
}
```

```asm
; idt_flush.asm
global idt_flush
idt_flush:
    mov eax, [esp+4]
    lidt [eax]       ; load IDT register
    ret
```

The IDT has 256 slots: 0-31 are CPU exceptions, 32-47 are IRQs (remapped by PIC). Flags `0x8E` = present(1) + DPL(00) + always0(0) + 32-bit interrupt gate(1110).

USER: Write the ISR (Interrupt Service Routines) header and implementation. Define the registers struct, isr_handler_t type, and the isr_init function that sets up all 32 exception gates, remaps the PIC, and sets up all 16 IRQ gates. Include isr_register_handler.
BOT: ```c
// isr.h
#ifndef ISR_H
#define ISR_H

#include "types.h"

typedef struct registers {
    uint32_t ds;                                      /* data segment */
    uint32_t edi, esi, ebp, esp, ebx, edx, ecx, eax; /* pusha order */
    uint32_t int_no, err_code;                        /* pushed by handler */
    uint32_t eip, cs, eflags, useresp, ss;            /* pushed by CPU */
} registers_t;

typedef void (*isr_handler_t)(registers_t *r);

void isr_init(void);
void isr_register_handler(uint8_t n, isr_handler_t handler);

#endif
```

```c
// isr.c
#include "isr.h"
#include "idt.h"
#include "string.h"
#include "ports.h"

static isr_handler_t isr_handlers[256];

/* Declare all 32 exception stubs and 16 IRQ stubs (defined in assembly) */
extern void isr0(void);  extern void isr1(void);  extern void isr2(void);
/* ... (isr3 through isr31) ... */
extern void isr31(void);
extern void irq0(void);  extern void irq1(void);  extern void irq2(void);
/* ... (irq3 through irq15) ... */
extern void irq15(void);

void isr_register_handler(uint8_t n, isr_handler_t handler) {
    isr_handlers[n] = handler;
}

/* Called from assembly stubs for CPU exceptions */
void isr_handler(registers_t *r) {
    if (isr_handlers[r->int_no] != NULL) {
        isr_handler_t handler = isr_handlers[r->int_no];
        handler(r);
    }
}

/* Called from assembly stubs for hardware IRQs */
void irq_handler(registers_t *r) {
    /* Send EOI to slave PIC if IRQ 8-15 (int 40-47) */
    if (r->int_no >= 40)
        outb(0xA0, 0x20);
    /* Always send EOI to master PIC */
    outb(0x20, 0x20);

    if (isr_handlers[r->int_no] != NULL) {
        isr_handler_t handler = isr_handlers[r->int_no];
        handler(r);
    }
}

void isr_init(void) {
    memset(isr_handlers, 0, sizeof(isr_handlers));

    /* Set up exception gates (0-31) */
    idt_set_gate(0,  (uint32_t)isr0,  0x08, 0x8E);
    idt_set_gate(1,  (uint32_t)isr1,  0x08, 0x8E);
    /* ... 2 through 31 ... */
    idt_set_gate(31, (uint32_t)isr31, 0x08, 0x8E);

    /* Remap PIC: master IRQ 0-7 -> INT 0x20-0x27, slave IRQ 8-15 -> INT 0x28-0x2F */
    outb(0x20, 0x11);  /* ICW1: init master */
    outb(0xA0, 0x11);  /* ICW1: init slave */
    outb(0x21, 0x20);  /* ICW2: master offset = 0x20 (32) */
    outb(0xA1, 0x28);  /* ICW2: slave offset = 0x28 (40) */
    outb(0x21, 0x04);  /* ICW3: master has slave on IRQ2 */
    outb(0xA1, 0x02);  /* ICW3: slave identity */
    outb(0x21, 0x01);  /* ICW4: x86 mode */
    outb(0xA1, 0x01);  /* ICW4: x86 mode */
    outb(0x21, 0x00);  /* Unmask all master IRQs */
    outb(0xA1, 0x00);  /* Unmask all slave IRQs */

    /* Set up IRQ gates (32-47) */
    idt_set_gate(32, (uint32_t)irq0,  0x08, 0x8E);
    idt_set_gate(33, (uint32_t)irq1,  0x08, 0x8E);
    /* ... 34 through 47 ... */
    idt_set_gate(47, (uint32_t)irq15, 0x08, 0x8E);
}
```

```asm
; isr_handlers.asm — Individual interrupt stubs
; Each stub pushes a dummy error code (if the CPU doesn't), then the interrupt
; number, then jumps to the common handler that saves registers and calls isr_handler

%macro ISR_NOERR 1
global isr%1
isr%1:
    push 0              ; dummy error code
    push %1             ; interrupt number
    jmp isr_common_stub
%endmacro

%macro ISR_ERR 1
global isr%1
isr%1:
    push %1             ; CPU already pushed error code
    jmp isr_common_stub
%endmacro

%macro IRQ_STUB 2
global irq%1
irq%1:
    push 0
    push %2             ; 32+%1
    jmp irq_common_stub
%endmacro

ISR_NOERR 0
ISR_NOERR 1
ISR_NOERR 2
ISR_NOERR 3
ISR_NOERR 4
ISR_NOERR 5
ISR_NOERR 6
ISR_NOERR 7
ISR_ERR   8   ; Double Fault has error code
ISR_NOERR 9
ISR_ERR   10  ; Invalid TSS
ISR_ERR   11  ; Segment Not Present
ISR_ERR   12  ; Stack Fault
ISR_ERR   13  ; General Protection Fault
ISR_ERR   14  ; Page Fault
ISR_NOERR 15
ISR_NOERR 16
ISR_ERR   17  ; Alignment Check
ISR_NOERR 18
ISR_NOERR 19
ISR_NOERR 20
ISR_NOERR 21
ISR_NOERR 22
ISR_NOERR 23
ISR_NOERR 24
ISR_NOERR 25
ISR_NOERR 26
ISR_NOERR 27
ISR_NOERR 28
ISR_NOERR 29
ISR_ERR   30
ISR_NOERR 31

IRQ_STUB 0, 32
IRQ_STUB 1, 33
IRQ_STUB 2, 34
IRQ_STUB 3, 35
IRQ_STUB 4, 36
IRQ_STUB 5, 37
IRQ_STUB 6, 38
IRQ_STUB 7, 39
IRQ_STUB 8, 40
IRQ_STUB 9, 41
IRQ_STUB 10, 42
IRQ_STUB 11, 43
IRQ_STUB 12, 44
IRQ_STUB 13, 45
IRQ_STUB 14, 46
IRQ_STUB 15, 47

isr_common_stub:
    pusha               ; save EAX, ECX, EDX, EBX, ESP, EBP, ESI, EDI
    mov ax, ds
    push eax
    mov ax, 0x10        ; load kernel data segment
    mov ds, ax
    mov es, ax
    mov fs, ax
    mov gs, ax
    
    call isr_handler
    
    pop eax
    mov ds, ax          ; restore segments
    mov es, ax
    mov fs, ax
    mov gs, ax
    popa
    add esp, 8          ; clean up error code and int number
    iret

irq_common_stub:
    pusha
    mov ax, ds
    push eax
    mov ax, 0x10
    mov ds, ax
    mov es, ax
    mov fs, ax
    mov gs, ax
    
    call irq_handler
    
    pop eax
    mov ds, ax
    mov es, ax
    mov fs, ax
    mov gs, ax
    popa
    add esp, 8
    iret
```

PIC remapping is essential because the PC's default IRQ mapping (IRQ0-7 → INT 0x08-0x0F) overlaps with CPU exception vectors. Remapping to 0x20-0x2F avoids the conflict.

USER: Write the VBE framebuffer driver (vbe.h and vbe.c). Parse framebuffer info from multiboot, implement vbe_putpixel (32-bit RGB), vbe_fillrect, vbe_clear, and double buffering via vbe_swap_buffers.
BOT: ```c
// vbe.h
#ifndef VBE_H
#define VBE_H

#include "types.h"
#include "multiboot.h"

typedef struct framebuffer {
    uint8_t  *addr;       /* pointer to pixel data */
    uint32_t  width;
    uint32_t  height;
    uint32_t  pitch;      /* bytes per scanline */
    uint8_t   bpp;
    uint32_t  size;       /* total buffer size */
} framebuffer_t;

void vbe_init(multiboot_info_t *mbt);
void vbe_putpixel(uint32_t x, uint32_t y, uint32_t color);
void vbe_fillrect(uint32_t x, uint32_t y, uint32_t w, uint32_t h, uint32_t color);
void vbe_clear(uint32_t color);
framebuffer_t* vbe_get_fb(void);
void vbe_swap_buffers(void);

#endif
```

```c
// vbe.c
#include "vbe.h"
#include "string.h"
#include "paging.h"

static framebuffer_t fb;
static framebuffer_t back_fb;
static uint8_t      *back_buffer = NULL;

void vbe_init(multiboot_info_t *mbt) {
    fb.addr   = (uint8_t*)(uint32_t)mbt->framebuffer_addr;
    fb.width  = mbt->framebuffer_width;
    fb.height = mbt->framebuffer_height;
    fb.pitch  = mbt->framebuffer_pitch;
    fb.bpp    = mbt->framebuffer_bpp;
    fb.size   = fb.height * fb.pitch;

    /* Allocate back buffer for double buffering (tear-free rendering) */
    back_buffer = (uint8_t*)0x400000;  /* 4MB mark — above kernel, below VGA */
    back_fb = fb;
    back_fb.addr = back_buffer;

    /* Identity-map framebuffer and back buffer */
    paging_identity_map((uint32_t)fb.addr,
                        (uint32_t)fb.addr + fb.size);
    paging_identity_map((uint32_t)back_buffer,
                        (uint32_t)back_buffer + fb.size);
}

void vbe_putpixel(uint32_t x, uint32_t y, uint32_t color) {
    if (x >= fb.width || y >= fb.height) return;
    uint32_t offset = y * fb.pitch + x * (fb.bpp / 8);
    *(uint32_t*)(back_fb.addr + offset) = color;
}

void vbe_fillrect(uint32_t x, uint32_t y, uint32_t w, uint32_t h, uint32_t color) {
    /* Clamp to screen bounds */
    if (x >= fb.width) x = fb.width - 1;
    if (y >= fb.height) y = fb.height - 1;
    if (x + w > fb.width) w = fb.width - x;
    if (y + h > fb.height) h = fb.height - y;

    for (uint32_t row = 0; row < h; row++) {
        for (uint32_t col = 0; col < w; col++) {
            uint32_t offset = (y + row) * fb.pitch + (x + col) * (fb.bpp / 8);
            *(uint32_t*)(back_fb.addr + offset) = color;
        }
    }
}

void vbe_clear(uint32_t color) {
    vbe_fillrect(0, 0, fb.width, fb.height, color);
}

framebuffer_t* vbe_get_fb(void) {
    return &fb;
}

void vbe_swap_buffers(void) {
    /* Copy back buffer to front buffer in one go */
    memcpy(fb.addr, back_buffer, fb.size);
}
```

Double buffering prevents screen tearing: all drawing goes to the back buffer, then `vbe_swap_buffers` copies the entire frame to the real framebuffer atomically. Color format is 0x00RRGGBB (24-bit color in a 32-bit word).

USER: Write a PS/2 keyboard driver with scancode-to-ASCII mapping, shift support, a circular buffer for queued input, and IRQ1 handler registration. Support keyboard_init, keyboard_has_char, keyboard_get_char.
BOT: ```c
// keyboard.h
#ifndef KEYBOARD_H
#define KEYBOARD_H

#include "types.h"

#define KEYBOARD_IRQ     1
#define KEY_BUF_SIZE     256

typedef enum {
    KEY_ESC = 0x1B, KEY_BACKSPACE = '\b', KEY_TAB = '\t',
    KEY_ENTER = '\n', KEY_SPACE = ' '
} keycode_t;

void    keyboard_init(void);
uint8_t keyboard_has_char(void);
char    keyboard_get_char(void);
uint8_t keyboard_is_key_down(keycode_t key);

#endif
```

```c
// keyboard.c
#include "keyboard.h"
#include "ports.h"
#include "isr.h"

/* Scancode Set 1 — standard US QWERTY mapping */
static uint8_t key_map[128] = {
    0,   0x1B, '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', '\b',
    '\t', 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '[', ']', '\n',
    0,   'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', '\'', '`',
    0,   '\\', 'z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/', 0,
    '*', 0,   ' ', 0,  /* 0x37-0x3A */
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  /* F1-F10 */
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  /* more */
};

/* Shifted versions */
static uint8_t shift_map[128] = {
    0,   0x1B, '!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '_', '+', '\b',
    '\t', 'Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', '{', '}', '\n',
    0,   'A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', ':', '"', '~',
    0,   '|', 'Z', 'X', 'C', 'V', 'B', 'N', 'M', '<', '>', '?', 0,
    '*', 0,   ' ', 0,
};

static uint8_t  shift = 0;
static uint16_t buf[KEY_BUF_SIZE];
static uint8_t  buf_head = 0;
static uint8_t  buf_tail = 0;

static void keyboard_callback(registers_t *r) {
    (void)r;
    uint8_t scancode = inb(0x60);  /* read scancode from keyboard data port */

    /* Left/Right Shift press */
    if (scancode == 0x2A || scancode == 0x36) { shift = 1; return; }
    /* Left/Right Shift release */
    if (scancode == 0xAA || scancode == 0xB6) { shift = 0; return; }

    /* Ignore key releases (high bit set) */
    if (scancode & 0x80) return;

    /* Look up ASCII — use shifted map if shift is held */
    uint16_t entry;
    if (shift) entry = (uint16_t)(shift_map[scancode]);
    else       entry = (uint16_t)(key_map[scancode]);

    /* If no mapping, encode raw scancode with high bit for debugging */
    if (entry == 0) entry = 0x8000 | scancode;

    /* Enqueue into circular buffer */
    uint8_t next = (buf_head + 1) % KEY_BUF_SIZE;
    if (next != buf_tail) {
        buf[buf_head] = entry;
        buf_head = next;
    }
}

void keyboard_init(void) {
    shift = 0;
    buf_head = buf_tail = 0;
    isr_register_handler(32 + KEYBOARD_IRQ, keyboard_callback);
}

uint8_t keyboard_has_char(void) {
    return buf_head != buf_tail;
}

char keyboard_get_char(void) {
    if (buf_head == buf_tail) return 0;
    uint16_t entry = buf[buf_tail];
    buf_tail = (buf_tail + 1) % KEY_BUF_SIZE;
    if (entry & 0x8000) return 0;  /* raw scancode, no ASCII mapping */
    return (char)(entry & 0xFF);
}
```

The circular buffer prevents key loss during burst input. `isr_register_handler(32 + KEYBOARD_IRQ, ...)` registers the handler for IRQ1 at the remapped interrupt number. The high-bit check on scancodes filters out key releases (only processes presses).

USER: Write a PS/2 mouse driver that initializes the mouse, reads 3-byte PS/2 packets, tracks position with acceleration, handles button state, and draws a pixel cursor. Use IRQ12.
BOT: ```c
// mouse.h
#ifndef MOUSE_H
#define MOUSE_H

#include "types.h"

#define MOUSE_IRQ 12

typedef struct mouse_state {
    int32_t x, y;
    uint8_t left_button;
    uint8_t right_button;
    uint8_t middle_button;
} mouse_state_t;

void mouse_init(void);
mouse_state_t* mouse_get_state(void);
void mouse_draw_cursor(void);

#endif
```

```c
// mouse.c
#include "mouse.h"
#include "vbe.h"
#include "ports.h"
#include "isr.h"

static mouse_state_t mouse = {400, 300, 0, 0, 0};
static uint8_t  mouse_cycle = 0;
static uint8_t  mouse_bytes[3];

/* Wait for PS/2 controller to be ready for write/read */
static inline void mouse_wait_write(void) {
    while (inb(0x64) & 0x02) {}  /* wait for input buffer empty */
}
static inline void mouse_wait_read(void) {
    while (!(inb(0x64) & 0x01)) {} /* wait for output buffer full */
}
static void mouse_write(uint8_t val) {
    mouse_wait_write();
    outb(0x64, 0xD4);  /* tell controller next byte is for mouse */
    mouse_wait_write();
    outb(0x60, val);
}
static uint8_t mouse_read(void) {
    mouse_wait_read();
    return inb(0x60);
}

static void mouse_handler(registers_t *r) {
    (void)r;
    uint8_t status = inb(0x64);

    /* Only process if data is from the mouse (bit 5 set) */
    if (!(status & 0x01)) return;
    if (!(status & 0x20)) return;

    uint8_t data = inb(0x60);

    switch (mouse_cycle) {
    case 0:
        /* First byte: flags. Bit 3 must be 1 (always set in PS/2 packets) */
        if (!(data & 0x08)) break;
        mouse_bytes[0] = data;
        mouse_cycle++;
        break;
    case 1:
        mouse_bytes[1] = data;  /* X movement */
        mouse_cycle++;
        break;
    case 2:
        mouse_bytes[2] = data;  /* Y movement */
        mouse_cycle = 0;

        /* Button state — bits 0,1,2 of first byte */
        mouse.left_button   = mouse_bytes[0] & 0x01;
        mouse.right_button  = mouse_bytes[0] & 0x02;
        mouse.middle_button = mouse_bytes[0] & 0x04;

        /* Sign-extend delta values if overflow bits are set */
        int32_t dx = (int32_t)mouse_bytes[1];
        int32_t dy = (int32_t)mouse_bytes[2];
        if (mouse_bytes[0] & 0x10) dx |= 0xFFFFFF00;
        if (mouse_bytes[0] & 0x20) dy |= 0xFFFFFF00;

        dy = -dy;  /* Y axis is inverted in PS/2 */

        framebuffer_t *fb = vbe_get_fb();
        mouse.x += dx;
        mouse.y += dy;

        /* Clamp to screen */
        if (mouse.x < 0) mouse.x = 0;
        if (mouse.y < 0) mouse.y = 0;
        if ((uint32_t)mouse.x >= fb->width)  mouse.x = (int32_t)(fb->width - 1);
        if ((uint32_t)mouse.y >= fb->height) mouse.y = (int32_t)(fb->height - 1);
        break;
    }
}

void mouse_init(void) {
    mouse.x = 400; mouse.y = 300;
    mouse.left_button = mouse.right_button = mouse.middle_button = 0;
    mouse_cycle = 0;

    /* Enable auxiliary PS/2 device (mouse) */
    mouse_wait_write();
    outb(0x64, 0xA8);

    /* Get current controller configuration byte */
    mouse_wait_write();
    outb(0x64, 0x20);
    mouse_wait_read();
    uint8_t status = inb(0x60);

    /* Enable mouse interrupts (bit 1) and disable translation (bit 5) */
    status |=  0x02;
    status &= ~0x20;

    mouse_wait_write();
    outb(0x64, 0x60);
    mouse_wait_write();
    outb(0x60, status);

    /* Mouse initialization sequence */
    mouse_write(0xF6);  /* Set defaults */
    mouse_read();       /* ACK */

    mouse_write(0xF3);  /* Set sample rate */
    mouse_write(200);   /* 200 samples/sec */
    mouse_read();

    mouse_write(0xF4);  /* Enable data reporting */
    mouse_read();

    /* Register IRQ12 handler */
    isr_register_handler(32 + MOUSE_IRQ, mouse_handler);
}

mouse_state_t* mouse_get_state(void) {
    return &mouse;
}

void mouse_draw_cursor(void) {
    framebuffer_t *fb = vbe_get_fb();
    int32_t mx = mouse.x;
    int32_t my = mouse.y;

    if (mx < 0 || my < 0 || (uint32_t)mx >= fb->width || (uint32_t)my >= fb->height)
        return;

    /* Classic arrow cursor — 12x16 pixels */
    for (uint32_t row = 0; row < 16; row++) {
        for (uint32_t col = 0; col < 12; col++) {
            /* Skip the "notch" in the cursor tail */
            if (row >= 12 && col >= 4 && row < 14 && col < 10)
                continue;
            /* Arrow shape: filled top-left triangle */
            if (!((row < 2) || (col == 0) || (col == 1) ||
                  (row == col + 1) || (row == col + 2)))
                continue;
            vbe_putpixel((uint32_t)(mx + (int32_t)col),
                         (uint32_t)(my + (int32_t)row), 0xFFFFFF);
        }
    }
}
```

PS/2 mouse packets are 3 bytes: [Y overflow|X overflow|Y sign|X sign|always1|Middle|Right|Left] [X delta] [Y delta]. The `0x08` bit check is critical — it validates the packet is synchronized.

USER: Write a PIT (Programmable Interval Timer) driver. Configure channel 0 at a given frequency, maintain a tick counter, implement timer_sleep for millisecond delays, and register the IRQ0 handler.
BOT: ```c
// timer.h
#ifndef TIMER_H
#define TIMER_H

#include "types.h"

void     timer_init(uint32_t frequency_hz);
uint32_t timer_get_ticks(void);
void     timer_sleep(uint32_t milliseconds);

#endif
```

```c
// timer.c
#include "timer.h"
#include "ports.h"
#include "isr.h"

static volatile uint32_t tick = 0;
static uint32_t freq = 0;

static void timer_callback(registers_t *r) {
    (void)r;
    tick++;
}

void timer_init(uint32_t f) {
    freq = f;
    tick = 0;

    /* PIT channel 0, mode 3 (square wave), 16-bit binary */
    uint32_t divisor = 1193180 / f;   /* PIT base clock = 1.19318 MHz */

    outb(0x43, 0x36);                 /* command byte */
    outb(0x40, (uint8_t)(divisor & 0xFF));       /* low byte */
    outb(0x40, (uint8_t)((divisor >> 8) & 0xFF)); /* high byte */

    isr_register_handler(32, timer_callback);     /* IRQ0 -> INT 32 */
}

uint32_t timer_get_ticks(void) {
    return tick;
}

void timer_sleep(uint32_t ms) {
    uint32_t start = tick;
    uint32_t target_ticks = (ms * freq) / 1000;
    if (target_ticks == 0) target_ticks = 1;
    while (tick - start < target_ticks) {
        __asm__ volatile ("hlt");  /* halt CPU until next interrupt */
    }
}
```

The PIT uses a 1.19318 MHz base clock. For a 100Hz timer: divisor = 1193180 / 100 = 11931. The `hlt` instruction in `timer_sleep` saves power by halting the CPU until the next interrupt wakes it.

USER: Write a simple paging implementation for a 32-bit OS. Support identity mapping, page directory and page table structs with C bitfields, and the assembly routine to load CR3 and enable paging via CR0.
BOT: ```c
// paging.h
#ifndef PAGING_H
#define PAGING_H

#include "types.h"

#define PAGE_SIZE 4096

typedef struct page_directory_entry {
    uint32_t present    : 1;   /* 1 = page is in memory */
    uint32_t rw         : 1;   /* 1 = read/write, 0 = read-only */
    uint32_t user       : 1;   /* 1 = user accessible (ring 3) */
    uint32_t wthrough   : 1;   /* write-through caching */
    uint32_t cache_dis  : 1;   /* cache disable */
    uint32_t accessed   : 1;   /* set by CPU on access */
    uint32_t dirty      : 1;   /* set by CPU on write (only for PTEs) */
    uint32_t page_size  : 1;   /* 0 = 4KB pages, 1 = 4MB pages */
    uint32_t global     : 1;   /* global page (not flushed on CR3 reload) */
    uint32_t available  : 3;   /* OS-defined */
    uint32_t frame      : 20;  /* physical page frame address (4KB aligned) */
} __attribute__((packed)) page_directory_entry_t;

typedef struct page_table_entry {
    uint32_t present    : 1;
    uint32_t rw         : 1;
    uint32_t user       : 1;
    uint32_t wthrough   : 1;
    uint32_t cache_dis  : 1;
    uint32_t accessed   : 1;
    uint32_t dirty      : 1;
    uint32_t pat        : 1;   /* Page Attribute Table */
    uint32_t global     : 1;
    uint32_t available  : 3;
    uint32_t frame      : 20;
} __attribute__((packed)) page_table_entry_t;

typedef struct page_directory {
    page_directory_entry_t entries[1024];
} __attribute__((aligned(4096))) page_directory_t;

typedef struct page_table {
    page_table_entry_t entries[1024];
} __attribute__((aligned(4096))) page_table_t;

void paging_init(void);
void paging_enable(void);
void paging_identity_map(uint32_t start, uint32_t end);

#endif
```

```c
// paging.c
#include "paging.h"
#include "string.h"

static page_directory_t *page_dir = NULL;
static page_table_t     *page_tbl = NULL;

extern void paging_load_directory(uint32_t dir_addr);
extern void paging_enable_paging(void);

void paging_init(void) {
    /* Allocate page directory at a fixed address (above kernel) */
    page_dir = (page_directory_t*)0x200000;  /* 2MB */
    page_tbl = (page_table_t*)0x201000;      /* 2MB + 4KB */

    memset(page_dir, 0, sizeof(page_directory_t));
    memset(page_tbl, 0, sizeof(page_table_t));

    /* Set up identity mapping for first 4MB (1024 pages * 4KB) */
    for (uint32_t i = 0; i < 1024; i++) {
        page_tbl->entries[i].present  = 1;
        page_tbl->entries[i].rw       = 1;
        page_tbl->entries[i].frame    = i;  /* page i maps to frame i */
    }

    /* Point first PDE to our page table */
    page_dir->entries[0].present = 1;
    page_dir->entries[0].rw      = 1;
    page_dir->entries[0].frame   = (uint32_t)page_tbl >> 12;
}

void paging_identity_map(uint32_t start, uint32_t end) {
    /* Identity-map additional ranges (e.g., framebuffer) */
    uint32_t start_frame = start / PAGE_SIZE;
    uint32_t end_frame   = (end + PAGE_SIZE - 1) / PAGE_SIZE;

    for (uint32_t frame = start_frame; frame < end_frame; frame++) {
        uint32_t pde_idx = frame / 1024;
        uint32_t pte_idx = frame % 1024;

        /* Allocate a new page table if needed */
        if (!page_dir->entries[pde_idx].present) {
            page_table_t *new_tbl = (page_table_t*)(0x202000 + pde_idx * PAGE_SIZE);
            memset(new_tbl, 0, sizeof(page_table_t));
            page_dir->entries[pde_idx].present = 1;
            page_dir->entries[pde_idx].rw      = 1;
            page_dir->entries[pde_idx].frame   = (uint32_t)new_tbl >> 12;
        }
    }
}

void paging_enable(void) {
    paging_load_directory((uint32_t)page_dir);
    paging_enable_paging();
}
```

```asm
; paging_asm.asm
global paging_load_directory
paging_load_directory:
    mov eax, [esp+4]
    mov cr3, eax        ; load page directory base
    ret

global paging_enable_paging
paging_enable_paging:
    mov eax, cr0
    or  eax, 0x80000000 ; set PG bit (bit 31)
    mov cr0, eax
    ret
```

Identity mapping means virtual address X maps to physical address X. This is the simplest setup for a kernel — every pointer "just works" after paging is enabled because the mapping is 1:1 for the mapped range.

USER: Write a string library for a freestanding kernel. Implement strlen, strcmp, strncmp, strcpy, strncpy, memset, memcpy, and memcmp without any standard library dependencies.
BOT: ```c
// string.h
#ifndef STRING_H
#define STRING_H

#include "types.h"

size_t strlen(const char *str);
int    strcmp(const char *a, const char *b);
int    strncmp(const char *a, const char *b, size_t n);
char*  strcpy(char *dst, const char *src);
char*  strncpy(char *dst, const char *src, size_t n);
void*  memset(void *ptr, uint8_t value, size_t num);
void*  memcpy(void *dst, const void *src, size_t num);
int    memcmp(const void *a, const void *b, size_t num);

#endif
```

```c
// string.c
#include "string.h"

size_t strlen(const char *str) {
    size_t len = 0;
    while (str[len]) len++;
    return len;
}

int strcmp(const char *a, const char *b) {
    while (*a && (*a == *b)) { a++; b++; }
    return *(const unsigned char*)a - *(const unsigned char*)b;
}

int strncmp(const char *a, const char *b, size_t n) {
    while (n && *a && (*a == *b)) { n--; a++; b++; }
    if (n == 0) return 0;
    return *(const unsigned char*)a - *(const unsigned char*)b;
}

char* strcpy(char *dst, const char *src) {
    char *orig = dst;
    while ((*dst++ = *src++));
    return orig;
}

char* strncpy(char *dst, const char *src, size_t n) {
    char *orig = dst;
    while (n && (*dst++ = *src++)) n--;
    while (n--) *dst++ = '\0';
    return orig;
}

void* memset(void *ptr, uint8_t value, size_t num) {
    uint8_t *p = (uint8_t*)ptr;
    while (num--) *p++ = value;
    return ptr;
}

void* memcpy(void *dst, const void *src, size_t num) {
    uint8_t *d = (uint8_t*)dst;
    const uint8_t *s = (const uint8_t*)src;
    while (num--) *d++ = *s++;
    return dst;
}

int memcmp(const void *a, const void *b, size_t num) {
    const uint8_t *pa = (const uint8_t*)a;
    const uint8_t *pb = (const uint8_t*)b;
    while (num--) {
        if (*pa != *pb) return *pa - *pb;
        pa++; pb++;
    }
    return 0;
}
```

All functions use raw pointer arithmetic with no libc dependencies — essential for `-nostdlib` kernel builds. `memset` and `memcpy` are byte-by-byte for simplicity; real kernels often optimize with `rep movsb` or word-aligned copies.

USER: Write a simple GUI drawing library that renders text using an 8x8 bitmap font. Implement gui_draw_string (font rendering), gui_draw_bootscreen (a loading bar), and gui_draw_desktop (background). Use the VBE framebuffer.
BOT: ```c
// gui.h
#ifndef GUI_H
#define GUI_H

#include "types.h"

void gui_draw_desktop(void);
void gui_draw_bootscreen(void);
void gui_draw_string(uint32_t x, uint32_t y, const char *str, uint32_t color);

#endif
```

```c
// gui.c
#include "gui.h"
#include "vbe.h"
#include "font8x8.h"  /* 8x8 bitmap font: font8x8[char][row] = bitmask */

#define COLOR_DESKTOP_BG    0x00316AC5  /* Windows XP-style blue */
#define COLOR_BOOT_BG       0x00000000  /* Black */

void gui_draw_string(uint32_t x, uint32_t y, const char *str, uint32_t color) {
    while (*str) {
        uint8_t c = (uint8_t)*str;
        if (c > 127) c = 0;  /* clamp to ASCII */
        
        /* Render each row of the 8x8 glyph */
        for (uint32_t row = 0; row < 8; row++) {
            uint8_t line = font8x8[c][row];
            for (uint32_t col = 0; col < 8; col++) {
                if (line & (1 << (7 - col))) {
                    vbe_putpixel(x + col, y + row, color);
                }
            }
        }
        x += 8;  /* advance 8 pixels per character */
        str++;
    }
}

void gui_draw_bootscreen(void) {
    framebuffer_t *fb = vbe_get_fb();

    /* Black background */
    vbe_clear(COLOR_BOOT_BG);

    /* Centered loading bar */
    uint32_t bar_x = (fb->width - 300) / 2;
    uint32_t bar_y = fb->height / 2 + 40;

    /* "Starting MyOS..." */
    gui_draw_string(bar_x, fb->height / 2 - 30,
        "Starting MyOS...", 0x00FFFFFF);

    /* Progress bar background */
    vbe_fillrect(bar_x, bar_y, 300, 24, 0x00404040);

    /* Animated blue progress blocks (3D effect with highlight) */
    for (uint32_t i = 0; i < 12; i++) {
        uint32_t bx = bar_x + 4 + i * 24;
        vbe_fillrect(bx, bar_y + 4, 20, 16, 0x003163C6);
        vbe_fillrect(bx, bar_y + 4, 20, 2,  0x005BA1E8);  /* highlight bar */
    }

    /* Copyright text */
    gui_draw_string(bar_x, bar_y + 36,
        "Copyright (C) MyOS Corporation", 0x00A0A0A0);
}

void gui_draw_desktop(void) {
    framebuffer_t *fb = vbe_get_fb();

    /* Gradient background: top color to bottom */
    for (uint32_t y = 0; y < fb->height; y++) {
        /* Interpolate between top blue and bottom lighter blue */
        uint8_t r = 0x31 + (uint8_t)((0x5B - 0x31) * y / fb->height);
        uint8_t g = 0x6A + (uint8_t)((0xA1 - 0x6A) * y / fb->height);
        uint8_t b = 0xC5 + (uint8_t)((0xE8 - 0xC5) * y / fb->height);
        uint32_t color = (r << 16) | (g << 8) | b;
        vbe_fillrect(0, y, fb->width, 1, color);
    }

    gui_draw_string(20, 20, "My Operating System", 0x00FFFFFF);
}
```

The 8x8 font is stored as a 2D array: `font8x8[character][row]` where each row is a bitmask (1=foreground, 0=background). The bootscreen renders a Windows XP-style loading bar with 12 blocks and a highlight strip for a 3D effect. Desktop uses a vertical gradient by interpolating RGB per scanline.

USER: Write a window manager for a simple GUI OS. Support window creation with title bars, close/minimize/maximize buttons, Z-ordering, focus management, click handling, keyboard input dispatch, a taskbar with a Start button, desktop icons, and a start menu. Use the framebuffer for rendering.
BOT: ```c
// wm.h
#ifndef WM_H
#define WM_H

#include "types.h"

#define MAX_WINDOWS        32
#define TITLE_BAR_H        22
#define WIN_BORDER          3
#define WIN_BTN_SIZE       16
#define WIN_BTN_MARGIN      4

#define TASKBAR_H          30
#define START_BTN_W        82

/* Window color constants */
#define COLOR_TITLEBAR      0x003163C6
#define COLOR_TITLEBAR_INACTIVE 0x00808080
#define COLOR_WIN_BG        0x00FFFFFF
#define COLOR_TASKBAR       0x002B5797
#define COLOR_START_MENU    0x00F0F0F0
#define COLOR_DESKTOP_TOP   0x003163C6
#define COLOR_DESKTOP_BOT   0x005BA1E8

typedef struct window window_t;

typedef void (*win_draw_fn)(window_t *win);
typedef void (*win_click_fn)(window_t *win, int32_t mx, int32_t my);
typedef void (*win_key_fn)(window_t *win, char c);

struct window {
    int32_t      x, y;
    uint32_t     width, height;
    char         title[64];
    uint8_t      visible;
    uint8_t      focused;
    uint8_t      minimized;
    uint8_t      maximized;
    uint8_t      has_close;
    uint8_t      has_minimize;
    uint8_t      has_maximize;
    uint8_t      draggable;
    win_draw_fn  on_draw;     /* app's custom render function */
    win_click_fn on_click;    /* app's click handler */
    win_key_fn   on_key;      /* app's keyboard handler */
    void        *user_data;
    window_t    *next;        /* linked list for Z-order */
};

typedef struct desktop_icon {
    int32_t x, y;
    char    label[32];
    void  (*action)(void);
} desktop_icon_t;

void wm_init(void);
window_t* wm_create_window(int32_t x, int32_t y, uint32_t w, uint32_t h,
                           const char *title, win_draw_fn draw,
                           win_click_fn click, win_key_fn key,
                           uint8_t close, uint8_t minimize, uint8_t maximize);
void wm_close_window(window_t *win);
void wm_focus_window(window_t *win);
window_t* wm_get_focused(void);
void wm_draw_all(void);
void wm_process_events(void);
void wm_show_start_menu(void);
void wm_hide_start_menu(void);
uint8_t wm_start_menu_visible(void);
void wm_register_icon(int32_t ix, int32_t iy, const char *label,
                      void (*action)(void));
void wm_draw_window_frame(window_t *win);

#endif
```

The window manager manages a linked list of windows (Z-ordered), handles mouse events (click detection, drag, button hits), dispatches keyboard input to the focused window, and renders the desktop, taskbar, Start menu, and all windows.

Key algorithms in wm.c:
- **Click routing**: iterate window list from top-to-bottom, check if click is in window rect, handle title bar buttons vs client area
- **Drag**: on mouse-down in title bar, record offset; on mouse-move, update window position; on mouse-up, release
- **Z-order**: move clicked window to front of linked list
- **Rendering order**: desktop background → windows bottom-to-top → taskbar → start menu → mouse cursor
- **Window frame**: 3px border, 22px title bar with gradient, close (red X), minimize, maximize buttons
- **Taskbar**: 30px at bottom with Start button and window buttons

USER: Write the kernel main function that ties everything together: initialize GDT, IDT, ISR, paging, VBE, timer, draw bootscreen, init keyboard/mouse, init VFS and WM, enable interrupts, and enter the main event loop processing window manager events and keyboard input.
BOT: ```c
// kernel.c — Kernel entry point
#include "types.h"
#include "multiboot.h"
#include "gdt.h"
#include "idt.h"
#include "isr.h"
#include "paging.h"
#include "vbe.h"
#include "gui.h"
#include "wm.h"
#include "mouse.h"
#include "keyboard.h"
#include "timer.h"
#include "string.h"
#include "vfs.h"

void kernel_main(uint32_t magic, multiboot_info_t *mbt) {
    /* Validate GRUB boot */
    if (magic != MULTIBOOT_EAX_MAGIC)
        return;

    /* Core CPU setup */
    gdt_init();
    idt_init();
    isr_init();

    /* Memory management */
    paging_init();
    paging_enable();

    /* Video — parse framebuffer from multiboot */
    vbe_init(mbt);

    /* Timer — 100Hz (fires 100 times/sec) */
    timer_init(100);

    /* Show boot screen while initializing */
    gui_draw_bootscreen();
    vbe_swap_buffers();

    /* Input devices */
    keyboard_init();
    mouse_init();

    /* File system and window manager */
    vfs_init();
    wm_init();

    /* Enable interrupts — the system is now live */
    __asm__ volatile ("sti");

    /* Brief delay so the boot screen is visible */
    timer_sleep(2000);

    /* === MAIN EVENT LOOP === */
    for (;;) {
        __asm__ volatile ("sti");
        __asm__ volatile ("hlt");  /* sleep until next interrupt */

        /* Dispatch mouse events to window manager */
        wm_process_events();

        /* Dispatch keyboard input to focused window */
        if (keyboard_has_char()) {
            char c = keyboard_get_char();
            window_t *fw = wm_get_focused();
            if (fw && fw->on_key) {
                fw->on_key(fw, c);
            }
        }

        /* Render everything */
        wm_draw_all();

        /* Draw mouse cursor last (on top of everything) */
        mouse_draw_cursor();

        /* Present the frame */
        vbe_swap_buffers();
    }
}
```

The initialization order is critical:
1. GDT/IDT/ISR — must be first (CPU needs interrupt handling before anything else)
2. Paging — enables virtual memory before touching framebuffer addresses
3. VBE — must come after paging so framebuffer can be identity-mapped
4. Timer — needs ISR to be initialized
5. Bootscreen — first visual feedback to the user
6. Input devices — register IRQ handlers for keyboard (IRQ1) and mouse (IRQ12)
7. VFS, WM — high-level subsystems

The main loop is classic: sleep via `hlt` (wakes on any interrupt), process input, render, swap buffers. The `hlt` instruction is critical — without it the CPU would spin at 100% doing nothing.

USER: What is the overall architecture and directory structure for a complete 32-bit x86 OS project with GUI, window manager, and apps? Explain the build system, key components, and common patterns.
BOT: Here's the complete architecture for a 32-bit x86 hobby OS:

**Directory Structure:**
```
os/
├── Makefile              # Cross-compiler build system
├── linker.ld             # Linker script (loads kernel at 1MB)
├── src/
│   ├── boot/
│   │   └── boot.asm      # Multiboot header + entry point (NASM)
│   ├── kernel/
│   │   └── kernel.c      # kernel_main() — init + event loop
│   ├── cpu/
│   │   ├── gdt.c         # Global Descriptor Table
│   │   ├── gdt_flush.asm  # Assembly: lgdt + far jump
│   │   ├── idt.c         # Interrupt Descriptor Table
│   │   ├── idt_flush.asm  # Assembly: lidt
│   │   ├── isr.c         # ISR + IRQ handlers, PIC remapping
│   │   └── isr_handlers.asm  # 32 exception stubs + 16 IRQ stubs
│   ├── mem/
│   │   └── paging.c      # Page directory + identity mapping
│   ├── drivers/
│   │   ├── vbe.c         # VBE framebuffer + double buffering
│   │   ├── keyboard.c    # PS/2 keyboard (scancode → ASCII, circular buffer)
│   │   ├── mouse.c       # PS/2 mouse (3-byte packets, cursor rendering)
│   │   └── timer.c       # PIT (tick counter, sleep)
│   ├── gui/
│   │   ├── gui.c         # Drawing: strings, shapes, bootscreen, desktop
│   │   └── wm.c          # Window manager: windows, taskbar, start menu
│   ├── fs/
│   │   └── vfs.c         # Virtual filesystem (ramdisk or initrd)
│   ├── apps/
│   │   ├── calc.c        # Calculator
│   │   ├── notepad.c     # Text editor
│   │   ├── cmd.c         # Command shell
│   │   ├── explorer.c    # File explorer
│   │   └── taskmgr.c     # Task manager
│   ├── lib/
│   │   ├── string.c      # strlen, memcpy, memset, etc.
│   │   └── font8x8.c     # 8x8 bitmap font data
│   └── include/          # All headers matching above
│       ├── types.h, gdt.h, idt.h, isr.h, paging.h
│       ├── multiboot.h, ports.h, string.h
│       ├── vbe.h, keyboard.h, mouse.h, timer.h
│       ├── gui.h, wm.h, vfs.h, font8x8.h
└── iso/                  # ISO image directory (created by make iso)
    └── boot/grub/grub.cfg
```

**Build System Pattern:**
- Cross-compiler: `i686-elf-gcc` (not host GCC — kernel needs freestanding)
- Assembler: NASM with `-f elf32`
- Linker: `i686-elf-ld` with `-m elf_i386 -T linker.ld`
- CFLAGS: `-m32 -ffreestanding -fno-exceptions -nostdlib -nostdinc -Wall -Wextra -std=c11`
- ISO creation: `grub-mkrescue` with a minimal grub.cfg
- Run: `qemu-system-i386 -cdrom os.iso -m 128`

**Key Architectural Patterns:**

1. **Multiboot → kernel_main chain**: GRUB loads the kernel, boots it in 32-bit protected mode, passes framebuffer info in the multiboot struct.

2. **Hardware initialization order**: GDT → IDT → ISR → Paging → VBE → Timer → Bootscreen → Input → VFS → WM → `sti`

3. **Interrupt-driven input**: Keyboard/mouse use IRQ handlers that enqueue into circular buffers. The main loop dequeues and dispatches.

4. **Double buffering**: All drawing goes to a back buffer in memory. `vbe_swap_buffers` copies the entire frame to the real framebuffer in one shot — prevents tearing.

5. **Window manager Z-order**: Windows stored as a linked list. Top of list = frontmost. Click handling iterates top-to-bottom. Rendering iterates bottom-to-top.

6. **App model**: Each app is a callback-driven window: `on_draw` renders content, `on_click` handles mouse, `on_key` handles keyboard. The app just implements these callbacks and calls `wm_create_window`.

7. **No standard library**: Everything is freestanding. Even `strlen` and `memcpy` are handwritten. No `printf` — use `gui_draw_string` for output.

**Common Gotchas:**
- The PIC must be remapped (IRQ0→INT32 not IRQ0→INT8) or IRQs collide with CPU exceptions
- PS/2 mouse initialization requires specific command sequences and ACK reads
- VBE framebuffer address must be identity-mapped in page tables
- The GDT null descriptor is mandatory and must be entry 0
- `__attribute__((packed))` is essential on hardware-facing structs
- The multiboot `framebuffer_addr` is a 64-bit field — cast to 32-bit for 32-bit kernels

USER: Explain the four main kernel architecture types — monolithic, microkernel, hybrid, and exokernel — with their design tradeoffs, performance characteristics, and real-world examples of each.
BOT: ## Kernel Architecture Types

### 1. Monolithic Kernel
All OS services run in kernel space as a single binary. Device drivers, filesystems, networking, and process management share the same address space.

**Examples:** Linux, BSD, MS-DOS, classic UNIX

**Design:**
- Single address space — any kernel component can call any other directly via function calls
- No IPC overhead for kernel services
- Modules can be dynamically loaded (Linux `.ko`), but run in kernel space

**Pros:**
- Fastest possible performance — direct function calls, zero-copy between subsystems
- Simpler IPC model compared to message-passing microkernels
- Mature, well-understood design (40+ years of Linux evolution)

**Cons:**
- A bug in any driver can crash the entire kernel (no isolation between components)
- Large attack surface — every module can access everything
- Harder to formally verify correctness
- Monolithic codebases become enormous (Linux: 30M+ lines)

### 2. Microkernel
Only the absolute minimum runs in kernel space: address space management, thread scheduling, and IPC. Everything else (filesystems, networking, device drivers) runs as user-space servers.

**Examples:** MINIX, QNX, L4 family, seL4, GNU Hurd, Fuchsia (Zircon)

**Design:**
- Kernel provides: threads, address spaces, IPC channels, capability-based access control
- Drivers and services are isolated user-space processes
- All communication via message-passing IPC

**Pros:**
- Fault isolation: a crashing driver doesn't take down the kernel — restart it
- Smaller trusted computing base (TCB) — easier to formally verify (seL4 is fully verified)
- Better security model: capability-based access, principle of least privilege
- Modular by design — swap components without kernel rebuild

**Cons:**
- IPC overhead: every syscall becomes at least one message round-trip
- Context switch cost adds up — L4 tackled this with extremely optimized IPC (≈100 cycles on x86)
- Complex synchronization between user-space servers
- Historically slower (though modern implementations close the gap)

### 3. Hybrid Kernel
A compromise: most services run in kernel space (like monolithic) for performance, but some run in user space. The kernel itself is structured more modularly than a pure monolith.

**Examples:** Windows NT, macOS (XNU), Plan 9

**Design (XNU — macOS/iOS kernel):**
- Mach microkernel at the core (threads, IPC, VM)
- BSD layer on top (POSIX, networking, VFS) — runs in kernel space
- I/O Kit for drivers — C++ object-oriented driver framework in kernel space
- The "hybrid" is between Mach's message-passing and BSD's monolithic approach

**Pros:**
- Can optimize hot paths by keeping them in kernel space
- More structured internally than pure monoliths
- Backward-compatible with existing driver ecosystems

**Cons:**
- Not as clean as microkernel, not as fast as pure monolith
- Complexity from combining two paradigms
- Still has a large TCB

### 4. Exokernel
The most radical design: the kernel provides only secure multiplexing of hardware. All abstractions (filesystems, VM policies, scheduling policies) live in user-space library OSes (libOS).

**Examples:** MIT Exokernel, Nemesis, Drawbridge (Microsoft)

**Design:**
- Kernel exports raw hardware securely: "here's a disk block range, do what you want"
- Applications link against a libOS that implements the OS abstractions they need
- Different apps can use different libOSes — a database gets a custom filesystem, a web server gets a custom network stack

**Pros:**
- Maximum flexibility — applications control resource management
- No one-size-fits-all abstractions imposed by the kernel
- Can achieve near-bare-metal performance

**Cons:**
- Extremely complex to implement securely (secure multiplexing is the hard part)
- No standardization across applications
- Very few real-world deployments

### 5. Unikernel (Bonus)
A single-address-space design where the application, its language runtime, and a minimal OS layer are compiled into one binary that runs directly on the hypervisor.

**Examples:** MirageOS (OCaml), IncludeOS (C++), OSv (Java)

### Performance Comparison (approximate syscall latency):
```
Linux (monolithic):     ~100-200 cycles for getpid()
L4 (microkernel):       ~100 cycles for IPC round-trip
seL4 (microkernel):     ~150 cycles for IPC
XNU (hybrid):           ~200-400 cycles for Mach-based calls
```

### When to Use Each:
- **Monolithic**: General-purpose OS, maximum performance, wide hardware support (Linux everywhere)
- **Microkernel**: Safety-critical systems, formal verification required, more hardware partitioning (QNX in cars, seL4 in drones/medical)
- **Hybrid**: Consumer OS with legacy driver ecosystem (Windows, macOS)
- **Exokernel/Unikernel**: Specialized high-performance servers, cloud workloads

USER: Explain virtual memory management in depth. Cover page tables across architectures (x86_64 4-level/5-level, ARM64, RISC-V), TLB operation, page faults, demand paging, copy-on-write, memory-mapped files, and kernel memory allocators (buddy, slab, SLUB).
BOT: ## Virtual Memory Management — Deep Dive

### The Core Concept
Virtual memory creates an abstraction where each process sees its own linear address space (e.g., 0 to 2^48-1 on x86_64) while physical RAM is shared and fragmented. The MMU (Memory Management Unit) translates every virtual address to a physical address using page tables.

### Page Table Walk — x86_64 (4-Level Paging)
A 48-bit virtual address is split into 5 parts:

```
| 63-48 | 47-39 | 38-30 | 29-21 | 20-12 | 11-0 |
| sign  | PML4  | PDPT  | PD    | PT    | off  |
| ext   | 9 bits| 9 bits| 9 bits| 9 bits| 12   |
```

The MMU walks 4 levels:
1. **CR3 register** → PML4 table (512 entries × 512GB each)
2. **PML4 entry** → Page Directory Pointer Table (512 entries × 1GB each)
3. **PDPT entry** → Page Directory (512 entries × 2MB each)
4. **PD entry** → Page Table (512 entries × 4KB each)
5. **PT entry** → Physical page frame + 12-bit offset

Each entry is 8 bytes (64 bits) and contains:
```
Bits 0:   Present (must be 1)
Bit 1:    Read/Write (0=read-only)
Bit 2:    User/Supervisor (0=supervisor only)
Bit 3:    Page-Level Write-Through
Bit 4:    Page-Level Cache Disable
Bit 5:    Accessed (set by CPU on access)
Bit 6:    Dirty (set by CPU on write)
Bit 7:    Page Size (0=4KB, 1=2MB/1GB huge page)
Bit 8:    Global (not flushed on CR3 reload)
Bits 12-51: Physical page frame number (40 bits for 52-bit physical addressing)
Bit 63:   No-Execute (NX) — prevents code execution
```

**5-Level Paging (Intel Ice Lake+, 57-bit VA):**
Adds a P5 (PML5) level above PML4, giving 57-bit virtual addresses (128PB addressable). Controlled by CR4.LA57 bit.
```
| 56-48 | 47-39 | 38-30 | 29-21 | 20-12 | 11-0 |
| P5    | PML4  | PDPT  | PD    | PT    | off  |
```

### ARM64 Page Tables
ARM64 uses a different terminology but same concept:
- **Translation Granule**: 4KB, 16KB, or 64KB (selected at boot)
- With 4KB granule: 4-level walk (TTBR0_EL1/TTBR1_EL1 → L0 → L1 → L2 → L3)
- **TTBR0_EL1**: User-space page table base (lower VA)
- **TTBR1_EL1**: Kernel-space page table base (upper VA) — avoids flushing kernel TLB on context switch
- Descriptor format differs from x86 (ARM uses block/page descriptors with attribute fields)

### RISC-V Page Tables (Sv39, Sv48, Sv57)
RISC-V defines three paging modes:
- **Sv39**: 3-level, 39-bit VA, 512GB addressable (standard for RV64)
- **Sv48**: 4-level, 48-bit VA, 256TB addressable
- **Sv57**: 5-level, 57-bit VA (planned)

Page table entries use a consistent format: PPN (Physical Page Number) + flags (V=Valid, R=Read, W=Write, X=Execute, U=User, G=Global, A=Accessed, D=Dirty).

### TLB (Translation Lookaside Buffer)
The TLB is a cache of virtual-to-physical translations inside the MMU. Without it, every memory access would require 4-5 DRAM lookups.

**TLB Organization:**
- **ITLB**: Instruction fetch translations
- **DTLB**: Data access translations
- **STLB**: Shared second-level TLB (larger, slower)
- Typical: 64-entry L1 ITLB, 64-entry L1 DTLB, 1536-entry L2 STLB per core

**TLB Shootdown (SMP):**
When one CPU changes a page table, all CPUs must invalidate stale TLB entries. This is done via:
1. Send IPI (Inter-Processor Interrupt) to all CPUs currently running the process
2. Each CPU executes `invlpg addr` (x86) or `tlbi` (ARM) to flush the entry
3. This is expensive — why `munmap` on large ranges is slow

**TLB Coalescing / Batching:**
Linux batches TLB flushes: accumulate page table changes, then do one batch shootdown. This is the `mmu_gather` mechanism.

### Page Fault Handling
When the MMU can't translate an address, it raises a page fault (#PF, INT 14 on x86). The kernel's page fault handler checks CR2 (faulting address) and the error code:

```
Error code bits:
bit 0: Present (0=not-present, 1=protection violation)
bit 1: Write (0=read access, 1=write access)
bit 2: User (0=supervisor mode, 1=user mode)
bit 3: Reserved bit violation
bit 4: Instruction fetch
```

The fault handler then:
1. **Not-present + valid VMA**: Demand page — allocate frame, read from disk/file, map
2. **Not-present + no VMA (below stack)**: Stack expansion (up to `RLIMIT_STACK`)
3. **Write + read-only + COW**: Copy-on-write — duplicate the page
4. **Write + no VMA or wrong permissions**: SIGSEGV to process
5. **User + kernel-only page**: SIGSEGV (SMAP/SMEP violation)

### Demand Paging
Pages are allocated on first access, not at `mmap()` time:
```
mmap(file, 1GB, PROT_READ, MAP_PRIVATE)  // Creates VMA, ZERO pages allocated
ptr[0]  // Page fault → read page from file → map to frame → return
```

This is why `mmap` is O(1) for the kernel — it just creates a VMA. The actual work happens lazily on access.

### Copy-on-Write (COW)
When `fork()` creates a child process:
1. Child gets a copy of the parent's page tables
2. All pages in both processes are marked **read-only**
3. On first write by either process:
   - Page fault (write to read-only page)
   - Kernel allocates a new physical frame
   - Copies the page contents
   - Updates the faulting process's page table to point to the new frame (writable)
   - The other process retains the original (still read-only if it hasn't written yet)

This is why `fork()` is fast — no actual copying happens. Linux optimizes further with `vfork()` and `clone(CLONE_VM)`.

### Kernel Memory Allocators

**Buddy Allocator (Page Allocator):**
Manages physical pages in power-of-2 blocks. API: `alloc_pages(order)`, `free_pages(page, order)`.

```
Free lists: order 0 (4KB), order 1 (8KB), order 2 (16KB), ... order 10 (4MB)
Allocation: find smallest block ≥ requested size, split if necessary
Free: coalesce with buddy if free → move up to larger order
```

Properties:
- External fragmentation: low (coalescing)
- Internal fragmentation: 50% worst-case (allocate 3KB → get 4KB)
- Fast: O(log n) with bitmaps

**Slab Allocator (Object Caching):**
Sits on top of the buddy allocator. Manages fixed-size objects for kernel data structures.

```c
struct kmem_cache *inode_cache = kmem_cache_create("inode", sizeof(struct inode), ...);
struct inode *ino = kmem_cache_alloc(inode_cache, GFP_KERNEL);
kmem_cache_free(inode_cache, ino);
```

Each cache maintains partial/full/empty slabs (contiguous pages divided into objects):
- **Full slab**: All objects in use
- **Partial slab**: Some free, some used
- **Empty slab**: All free (can be returned to buddy allocator)

**SLUB Allocator (Linux default since 2.6.23):**
Simplified slab design — no separate slab management structs. Merges per-CPU caching with NUMA awareness:
- Per-CPU partial lists for lockless fast-path allocation
- Defers complex operations (coalescing, NUMA rebalancing) to slow path
- Smaller metadata overhead than classic slab

### Huge Pages
- **2MB pages** (x86_64): Use PD entry with Page Size bit = 1 — skips one level of translation
- **1GB pages** (x86_64): Use PDPT entry with Page Size bit = 1 — skips two levels
- **Transparent Huge Pages (THP)**: Linux automatically promotes/demotes pages without application changes
- Benefits: Fewer TLB misses (1 entry covers 512× more memory), fewer page faults

### Memory-Mapped Files
The page cache and `mmap` share the same physical pages:
```c
// Both point to the same page cache pages
int fd = open("data.bin", O_RDONLY);
void *map = mmap(NULL, size, PROT_READ, MAP_PRIVATE, fd, 0);
// Accessing map[i] → page fault → read from file → map to PTE
// Another process mmap-ing the same file can share the page cache (MAP_SHARED)
```

KEY: `MAP_SHARED` writes go back to the file. `MAP_PRIVATE` uses COW — writes create a private copy.

USER: Explain process and thread management in depth. Cover scheduling algorithms (CFS, EEVDF, O(1), round-robin, real-time), context switching mechanics, synchronization primitives (spinlocks, mutexes, RCU, semaphores, rwlocks), IPC mechanisms, and how fork/exec work internally.
BOT: ## Process & Thread Management — Deep Dive

### Process vs Thread
- **Process**: Has its own address space (page tables), file descriptor table, signal handlers. Heavyweight.
- **Thread**: Shares the address space of its process. Has its own stack, register state, and (in Linux) its own `task_struct`. Lightweight.
- In Linux: Both are `task_struct`. Threads are just processes that share `mm_struct` (address space) and `files_struct` (file table) via `clone(CLONE_VM | CLONE_FILES | ...)`.

### Context Switching — The Mechanics
A context switch saves the current CPU state and loads another:

1. **Hardware context**: Stack pointer (RSP), instruction pointer (RIP), CR3 (page tables), segment registers, general-purpose registers
2. **`switch_to()` (Linux)**: Assembly macro that pushes RBP/RBX/R12-R15, swaps stack pointers, loads the new task's saved registers
3. **CR3 reload**: If switching to a different process (different address space), load new CR3 — flushes all non-global TLB entries
4. **FPU/SSE/AVX state**: Lazily saved (only saved when another task wants the FPU) via TS flag. Eagerly restored if XSAVES is available
5. **Switch time**: ~1-2μs on modern hardware (excluding cache/TLB effects)

The cost breakdown:
- Direct register save/restore: ~100ns
- FPU state (512 bytes AVX-512): ~20ns with XSAVES
- TLB refill after CR3 reload: 10-100μs (depends on working set)
- L1/L2 cache warmth loss: variable, can dominate

### Linux Scheduler — From O(1) to CFS to EEVDF

**O(1) Scheduler (Linux 2.4-2.6.22):**
- Two arrays per CPU: active and expired
- 140 priority levels (0-99 RT, 100-139 normal)
- Each level has a runqueue bitmap — find next task via `ffs()` (find first set bit) = O(1)
- When a task uses its time slice, move to expired array. Swap arrays when active is empty.
- Problems: Heuristics for interactive tasks were fragile and gameable

**CFS (Completely Fair Scheduler, Linux 2.6.23-6.5):**
Core idea: each task should get a fair share of CPU time proportional to its weight (nice value).

Data structure: Red-black tree ordered by `vruntime` — the amount of CPU time a task has received, weighted by its priority.

```c
// Simplified CFS pick_next:
struct task_struct *pick_next_task_cfs(void) {
    // Get leftmost node in red-black tree (lowest vruntime)
    struct sched_entity *se = rb_first(&cfs_rq->tasks_timeline);
    return task_of(se);
}

// Update vruntime on tick:
se->vruntime += delta_exec * NICE_0_LOAD / se->load.weight;
// Lower priority → higher weight denominator → vruntime grows faster → gets scheduled less
```

Key parameters:
- `sched_latency`: Target period for one scheduling cycle (default: 6ms)
- `sched_min_granularity`: Minimum time slice (default: 0.75ms)
- Time slice for task: `sched_latency * (task_weight / total_weight)`
- Task with nice -20 (weight 88761) gets 5.4× more CPU than nice 0 (weight 1024)

**EEVDF (Earliest Eligible Virtual Deadline First, Linux 6.6+):**
Replacement for CFS. Each task has a virtual deadline:
```
deadline = eligible_time + (time_slice / weight)
```
Tasks are sorted by virtual deadline in a min-heap. Pick the task with the earliest deadline that is "eligible" (its request time <= virtual time).

Benefits over CFS:
- Bounded latency: a task that sleeps a long time doesn't get unfairly large time slices
- Better for latency-sensitive workloads
- Simpler to reason about mathematically

### Real-Time Scheduling (Linux)
- **SCHED_FIFO**: Static priority, no time slicing. Runs until it blocks or is preempted by higher-priority RT task. 99 priority levels.
- **SCHED_RR**: Like FIFO but with time slices (round-robin among same-priority RT tasks)
- **SCHED_DEADLINE**: Earliest Deadline First (EDF) with bandwidth enforcement. Each task declares runtime, period, and deadline
- RT tasks always preempt CFS/EEVDF tasks

### Synchronization Primitives

**Spinlock (busy-waiting):**
```c
spin_lock(&lock);    // Disables preemption on UP, spins on SMP
// Critical section — must be short, must not sleep
spin_unlock(&lock);
```
- Implementation: atomic test-and-set + `pause` instruction in spin loop
- On x86: `lock bts` (atomic bit test and set) on the lock word
- Never hold a spinlock while calling a function that might sleep (scheduling while atomic → kernel panic)

**Mutex (sleeping lock):**
```c
mutex_lock(&lock);   // Can sleep — usable in process context only
// Critical section
mutex_unlock(&lock);
```
- Implementation: fastpath = atomic compare-and-swap, slowpath = add to wait queue + schedule()
- Priority inheritance available for RT (prevents priority inversion)

**RCU (Read-Copy-Update):**
Optimized for read-mostly data structures. Readers never block:
```c
// Reader:
rcu_read_lock();     // Preemption disable on non-preempt RCU
ptr = rcu_dereference(shared_ptr);  // Compiler barrier
use(ptr);
rcu_read_unlock();

// Writer:
new = copy_and_modify(old);
rcu_assign_pointer(shared_ptr, new);  // Atomic pointer update
synchronize_rcu();  // Wait for all readers to finish
kfree(old);         // Safe to free
```
- Readers pay near-zero overhead (just preempt disable/enable)
- Writer waits for a grace period (all CPUs have context-switched)
- Used for: routing tables, file descriptors, module unload, directory entry cache

**Semaphore:**
Generalized mutex with a count. `down()` decrements (blocks if zero), `up()` increments (wakes waiters). Used for resource counting, not mutual exclusion.

**Read-Write Lock:**
Multiple concurrent readers OR one writer. Starvation-prone if readers keep arriving. The `rwsem` variant in Linux is optimized but rarer (RCU replaced most rwlock use cases).

### fork() Internals
```c
pid_t fork(void);
```

1. `_do_fork()` → `copy_process()`:
   - Allocates new `task_struct`
   - Copies `thread_struct` (register state) — child resumes from same point
   - Copies `mm_struct` via `dup_mm()`: duplicate page tables, mark pages COW
   - Forks `files_struct` — child shares or copies file descriptors (depends on flags)
   - Forks `signal_struct` — separated signal handling
   - Assigns new PID
   - Sets child's `thread.sp` and `thread.ip` for first return
2. Parent gets child's PID. Child gets 0.
3. Both share physical pages (COW) until one writes.

### execve() Internals
```c
int execve(const char *filename, char *const argv[], char *const envp[]);
```

1. Load new ELF binary:
   - Read ELF header → parse program headers
   - Set up new address space: `mmap` for text (read-only, executable), data (read-write), BSS
   - Map the dynamic linker (`ld.so`) if dynamically linked
2. Set up new stack:
   - Push argv, envp, auxiliary vector (AT_PHDR, AT_ENTRY, AT_PAGESZ, ...)
   - Set RSP to new stack
3. Set RIP to ELF entry point (or `ld.so` for dynamic)
4. Most signal handlers reset to default
5. file descriptors preserved (unless FD_CLOEXEC)
6. PID stays the same (same process, new program)

### IPC Mechanisms Comparison
| Mechanism | Speed | Use Case | Notes |
|-----------|-------|----------|-------|
| Pipe | Medium | Parent-child, shell pipelines | Unidirectional stream, anonymous |
| FIFO (named pipe) | Medium | Unrelated processes | Has a filesystem name |
| Unix Domain Socket | Medium | Client-server on same host | Bidirectional, datagram or stream |
| Shared Memory | Fastest | Large data, real-time | Requires external sync |
| Message Queue | Slow-Medium | Structured messages | POSIX or SysV |
| Signals | Fast | Async notification | Limited data (just a number) |
| D-Bus | Slow | Desktop services | High-level, typed messages |
| io_uring (Linux) | Very Fast | Bulk I/O | Shared ring buffers, async |

USER: Explain system calls in depth. Cover the mechanism on x86_64 (syscall/sysret) vs ARM64 (SVC) vs RISC-V (ecall), the Linux syscall table, how parameters are passed, fast vs slow paths, VDSO, and how to add a custom syscall to Linux.
BOT: ## System Calls — Deep Dive

### The Mechanism — x86_64
Modern x86_64 uses `syscall`/`sysret` (replacing the old `int 0x80`):

```asm
; User-space syscall invocation (glibc does this)
mov rax, 0        ; syscall number (0 = read)
mov rdi, fd       ; arg1
mov rsi, buf      ; arg2
mov rdx, count    ; arg3
syscall           ; Transition to ring 0
; Returns: rax = return value, rcx/r11 clobbered
```

**What `syscall` does:**
1. Saves RIP → RCX, RFLAGS → R11
2. Loads CS from `MSR_STAR[47:32]` (kernel code segment, ring 0)
3. Loads RIP from `MSR_LSTAR` (syscall entry point address)
4. Clears IF (interrupt flag) — no interrupts in critical handler start
5. Switches to kernel stack (from `MSR_GS_BASE`, the per-CPU area)

**`sysret` (return to user):**
1. Restores RIP from RCX, RFLAGS from R11
2. Switches back to user CS/SS
3. Returns to ring 3

Total cost: ~70-100 cycles for the transition alone (warm cache).

### Register Convention
| Register | Purpose |
|----------|---------|
| RAX | Syscall number AND return value |
| RDI | 1st argument |
| RSI | 2nd argument |
| RDX | 3rd argument |
| R10 | 4th argument (replaces RCX — RCX is clobbered by syscall) |
| R8 | 5th argument |
| R9 | 6th argument |
| RCX | Clobbered (saved RIP) |
| R11 | Clobbered (saved RFLAGS) |

### ARM64 Syscalls
```asm
mov x8, #64       ; syscall number (64 = write)
mov x0, fd        ; arg1
mov x1, buf       ; arg2
mov x2, count     ; arg3
svc #0            ; Supervisor Call — exception to EL1
```

ARM64 uses `svc` (Supervisor Call). The immediate `#0` is conventional (Linux ignores it, reading the syscall number from X8). Return uses `eret`.

### RISC-V Syscalls
```asm
li a7, 64         ; syscall number
li a0, fd         ; arg1
li a1, buf        ; arg2
li a2, count      ; arg3
ecall             ; Environment Call — trap to M/S-mode
```

RISC-V uses `ecall` which traps to the next higher privilege mode (U→S or S→M). The syscall number is in A7, arguments in A0-A6.

### Linux Syscall Table
The kernel dispatches based on RAX (x86) or X8 (ARM):

```c
// arch/x86/entry/syscalls/syscall_64.tbl
0    common  read     sys_read
1    common  write    sys_write
2    common  open     sys_open
3    common  close    sys_close
...
```

This generates an array:
```c
typedef long (*sys_call_ptr_t)(const struct pt_regs *);
sys_call_ptr_t sys_call_table[__NR_syscall_max] = {
    [0] = sys_read,
    [1] = sys_write,
    [2] = sys_open,
    ...
};
```

The entry point (`entry_SYSCALL_64`) does:
1. Save all registers to `pt_regs` on kernel stack
2. Validate syscall number (must be < `NR_syscalls`)
3. Call `sys_call_table[rax](regs)`
4. Put return value in RAX within `pt_regs`
5. Check for pending signals, rescheduling
6. Restore registers and `sysret`

### Fast vs Slow Path
- **Fast path**: Simple syscall (e.g., `getpid`). No blocking, no complex logic. ~100-200 cycles.
- **Slow path**: Requires disk I/O, blocking, complex validation. The syscall itself is fast but then blocks in the kernel. The `-ENOSYS` overhead routes to a slow syscall handler.

### VDSO (Virtual Dynamic Shared Object)
The kernel maps a small shared library into every process's address space. It contains optimized implementations of frequently-called syscalls that can be done without a full context switch:

```c
// glibc's gettimeofday() actually calls into VDSO:
// The VDSO reads the time from a shared kernel page — no syscall needed!
```

VDSO syscalls that avoid context switches:
- `clock_gettime()` — reads `vsyscall_gtod_data` from kernel-mapped page
- `getcpu()` — reads CPU number from per-CPU area (RDTSCP or LSL on x86)
- `time()` — reads time from shared page

This is why `clock_gettime()` is ~20ns while a real syscall is ~100ns.

### Adding a Custom Syscall to Linux

```c
// 1. Add entry to syscall table
// arch/x86/entry/syscalls/syscall_64.tbl:
// 451  common  my_hello  sys_my_hello

// 2. Implement in kernel/
// kernel/my_syscall.c:
#include <linux/syscalls.h>
#include <linux/kernel.h>

SYSCALL_DEFINE1(my_hello, const char __user *, name) {
    char kname[256];
    
    // Must use copy_from_user for user-space pointers!
    if (strncpy_from_user(kname, name, sizeof(kname)) < 0)
        return -EFAULT;
    
    printk(KERN_INFO "Hello from %s!\n", kname);
    return 0;
}

// 3. User-space caller:
#include <unistd.h>
#include <sys/syscall.h>
#define __NR_my_hello 451

int main() {
    long ret = syscall(__NR_my_hello, "Kernel Dev");
    // Or via inline asm:
    // __asm__ volatile("syscall" : "=a"(ret) : "a"(451), "D"("Kernel Dev"));
}
```

Critical rules for syscall implementation:
- **Never trust user pointers**: Always `copy_from_user()` / `copy_to_user()` — they handle page faults gracefully
- **Validate all inputs**: Syscalls are the kernel's front door — every argument is attacker-controlled
- **Return -errno on failure**: The C library converts negative return to errno
- **Keep it simple**: Complex logic should be in a helper, the syscall is just the boundary

### Security Considerations
- **SMAP (Supervisor Mode Access Prevention)**: Kernel can't access user memory without `stac`/`clac` — prevents kernel accidentally dereferencing user pointers. `copy_from_user()` temporarily disables SMAP.
- **SMEP (Supervisor Mode Execution Prevention)**: Kernel can't execute user-space code — prevents ret2usr attacks
- **KPTI (Kernel Page Table Isolation)**: Originally for Meltdown mitigation. Kernel has minimal page table when running in user mode — only the entry/exit trampoline is mapped. Full kernel mapping only when actually in kernel mode.
- **seccomp**: Filters syscalls using BPF. Chrome uses `seccomp-bpf` to restrict renderer processes.

USER: Explain filesystem design in operating systems. Cover VFS layer, inodes, dentry cache, page cache, journaling, ext4 internals, FAT/exFAT, and modern filesystems like Btrfs and ZFS.
BOT: ## Filesystem Design — Deep Dive

### The VFS (Virtual File System) Layer
Linux's VFS provides a uniform interface for all filesystems. It defines four key object types:

**1. Superblock (`super_block`):** Represents a mounted filesystem. Contains:
- Device info, block size, max file size
- Pointer to root dentry
- List of all inodes for this filesystem
- Filesystem-specific private data
- Operations: `alloc_inode`, `destroy_inode`, `write_super`, `sync_fs`, `statfs`

**2. Inode (`inode`):** Represents a file (or directory, device, symlink). Contains:
- File type (regular, directory, symlink, block/char device, FIFO, socket)
- Permissions (mode, uid, gid)
- Size, timestamps (atime, mtime, ctime)
- Number of blocks, pointers to data blocks
- Filesystem-specific data (e.g., ext4 extent tree)
- Operations: `lookup`, `create`, `link`, `unlink`, `mkdir`, `rename`, `setattr`, `getattr`

**3. Dentry (`dentry`):** Directory entry cache — maps names to inodes. Key features:
- Hash table lookup: `d_hash()`/`d_compare` for case-insensitive filesystems
- `d_lookup()` is lockless RCU-based (very hot path)
- Negative dentries (caching "file not found") prevent repeated lookups for missing files
- Parents and children tracked for path resolution

**4. File (`file`):** Open file description. Per-process, not per-inode:
- Current position (`f_pos`)
- Open flags (O_RDONLY, O_NONBLOCK, ...)
- File operations: `read`, `write`, `llseek`, `mmap`, `ioctl`, `poll`, `fsync`, `flush`

Path resolution example — opening "/home/user/file.txt":
```
1. Start at current->fs->root (/) dentry
2. lookup("home") → dentry "home" → gets its inode
3. In "home" inode, lookup("user") → dentry "user"
4. In "user" inode, lookup("file.txt") → dentry "file.txt"
5. Create file struct, set f_inode = file.txt's inode
```

### Page Cache
The page cache is the bridge between filesystem and memory:
- Every file page accessed via `read()` or `mmap` lives in the page cache (radix tree, keyed by file + offset)
- `write()` writes to page cache pages (marked dirty), then `writeback` threads flush to disk
- `mmap(MAP_SHARED)` maps page cache pages directly into user space — no double buffering
- `O_DIRECT` bypasses the page cache entirely (used by databases that do their own caching)

### Journaling
Prevents filesystem corruption from crashes. Three modes:

**Write-Ahead Logging (Journal):**
Before modifying the filesystem, write a description of the changes to a circular journal area. After the journal write completes, apply the actual changes. On recovery, replay the journal.

**ext4 Journal Modes:**
- `data=journal`: All data AND metadata go through journal. Safest, slowest.
- `data=ordered` (default): Only metadata journaled. Data blocks written before metadata commit. Good balance.
- `data=writeback`: Only metadata journaled. Data may be written after journal commit. Fastest, risk of stale data after crash.

### ext4 Internals

**Block Groups:** The filesystem is divided into block groups (128MB typical). Each group has:
- Superblock copy (in group 0 and sparse groups)
- Group descriptor (block bitmap, inode bitmap, inode table location)
- Data blocks

**Extent Tree (replacing indirect blocks from ext2/3):**
```
struct ext4_extent {
    __le32 ee_block;    // First logical block
    __le16 ee_len;      // Number of blocks
    __le16 ee_start_hi; // Upper 16 bits of physical block
    __le32 ee_start_lo; // Lower 32 bits of physical block
};
```
An inode stores up to 4 extents directly. For more, it uses an Htree (B-tree variant) of extent index nodes. This is vastly more efficient than the old indirect block scheme for large files.

**ext4 Features:**
- 48-bit block numbers (1 EiB max filesystem, 16 TiB max file)
- Extents for efficient large file mapping
- Delayed allocation — batches block allocations for better contiguity
- Multi-block allocator — allocates contiguous runs in one operation
- Nanosecond timestamps
- Fast fsck via uninitialized block groups and flex block groups

### FAT/exFAT — Simple and Ubiquitous

**FAT (File Allocation Table):**
- Each cluster has an entry in the FAT table: next cluster in chain, EOF marker, or BAD cluster marker
- Directories are special files with 32-byte entries (8.3 name, attributes, start cluster, size)
- No journaling, no permissions, no symlinks, no hard links
- Very simple to implement — about 500 lines of C for minimal read-only

**exFAT improvements over FAT32:**
- 64-bit file sizes (removes 4GB limit)
- Cluster bitmap for faster free space allocation
- UTC timestamps with 10ms resolution (vs 2-second in FAT)
- No 8.3 naming restriction (255-character filenames)
- Checksums for directory entries

### Btrfs — Copy-on-Write Filesystem
- Everything is COW: modifying data writes new blocks, then atomically updates tree root
- B-tree architecture: extent allocation tree, checksum tree, subvolume tree, snapshot tree
- Snapshots: O(1) — just pin the old tree root, new writes go to new blocks (COW)
- Checksums on data AND metadata — detects bitrot
- Compression per-file (zlib, lzo, zstd)
- Built-in RAID (single, RAID0, RAID1, RAID10, RAID5, RAID6)
- Subvolumes: mountable namespaces within a filesystem

### ZFS — The 128-bit Filesystem
- Everything is a tree of blocks with SHA-256 checksums — self-healing
- Copy-on-write transactional model
- Integrated volume manager (ZVOL) and RAID (RAID-Z)
- Snapshots, clones, deduplication, compression
- ARC (Adaptive Replacement Cache) — sophisticated page cache with ghost lists
- 128-bit addressing — "never run out of space" (2^128 bytes)
- Send/receive for efficient replication

### Filesystem Comparison
| Feature | ext4 | Btrfs | ZFS | exFAT |
|---------|------|-------|-----|-------|
| Max Volume | 1 EiB | 16 EiB | 256 ZiB | 128 PiB |
| Max File | 16 TiB | 16 EiB | 16 EiB | 16 EiB |
| Journaling | Yes | COW | COW | No |
| Snapshots | No | Yes | Yes | No |
| Checksums | Metadata | Full | Full | No |
| Compression | No | Yes (zlib/lzo/zstd) | Yes (all) | No |
| Permissions | Unix | Unix | Unix/ACL | None |
| Simplicity | Moderate | Complex | Complex | Simple |

### Building a Simple VFS from Scratch
```c
// Minimal VFS interface
struct vnode {
    uint32_t    vno;        // Inode number
    uint32_t    type;       // VNODE_FILE, VNODE_DIR
    uint32_t    size;
    uint32_t    refcount;
    void       *fs_data;    // FS-specific data
};

struct vnode_ops {
    int (*read)(struct vnode *vn, void *buf, uint32_t offset, uint32_t size);
    int (*write)(struct vnode *vn, const void *buf, uint32_t offset, uint32_t size);
    int (*lookup)(struct vnode *dir, const char *name, struct vnode **result);
    int (*create)(struct vnode *dir, const char *name, uint32_t type);
    int (*unlink)(struct vnode *dir, const char *name);
};

struct filesystem {
    char name[32];
    struct vnode_ops *ops;
    struct vnode *(*mount)(uint32_t device);
};

// Register filesystem implementations
struct filesystem *fs_registry[8];
int vfs_register(const char *name, struct vnode_ops *ops);
struct vnode *vfs_open(const char *path);

// Each filesystem (ramfs, FAT, ext2) implements vnode_ops
// VFS layer dispatches based on the vnode's fs_data pointer
```

The VFS pattern is the same at any scale: abstract interface → concrete implementations → dispatch through operations table. This is the Strategy pattern applied to filesystems.

USER: Explain boot processes across architectures. Cover BIOS/MBR vs UEFI/GPT, the Linux boot sequence (GRUB2 → kernel → initramfs → systemd), UEFI services (Runtime vs Boot), ACPI tables, device tree on ARM, and how to write a UEFI application.
BOT: ## Boot Processes — Deep Dive

### BIOS/MBR (Legacy)
The traditional PC boot:
1. **Power-on → CPU reset vector at 0xFFFFFFF0** (16 bytes below 4GB)
2. **BIOS runs POST** (Power-On Self Test) — checks RAM, keyboard, storage
3. **BIOS scans for bootable devices** — checks MBR (first 512 bytes) for boot signature (0xAA55)
4. **Loads MBR to 0x7C00** and jumps to it (16-bit real mode!)
5. **MBR code** loads stage 1.5 or stage 2 bootloader from disk
6. **Bootloader** loads kernel, sets up protected/long mode

**MBR Layout:**
```
Offset  Size  Description
0x000   440   Bootstrap code area
0x1B8   4     Disk signature (optional)
0x1BC   2     Reserved (0x0000)
0x1BE   16    Partition entry 1
0x1CE   16    Partition entry 2
0x1DE   16    Partition entry 3
0x1EE   16    Partition entry 4
0x1FE   2     Boot signature (0xAA55)
```

Limitations:
- Only 4 primary partitions
- Max partition size: 2TB (32-bit LBA)
- Very little space for boot code (440 bytes)
- 16-bit real mode — very constrained environment

### UEFI/GPT (Modern)
UEFI replaces BIOS with a more capable firmware:

**UEFI Boot Sequence:**
1. **Platform Init (PI)**: SEC → PEI → DXE → BDS phases
2. **DXE (Driver Execution Environment)**: Loads device drivers, discovers hardware
3. **BDS (Boot Device Selection)**: Scans boot options (Boot#### variables in NVRAM)
4. **Finds EFI System Partition (ESP)** — a FAT32 partition with GUID `C12A7328-F81F-11D2-...`
5. **Loads EFI application** from `\EFI\BOOT\BOOTX64.EFI` (or OS-specific path)
6. **EFI app** loads the actual OS kernel

**GPT (GUID Partition Table):**
- Up to 128 partitions (no extended/logical nonsense)
- 64-bit LBA — max partition size 9.4 ZB
- Protective MBR at LBA 0 (prevents legacy tools from destroying the GPT)
- Primary GPT header at LBA 1, backup at last LBA
- Partition entries: 128 bytes each with type GUID, unique GUID, name (36 UTF-16 chars)

**UEFI Services:**
- **Boot Services**: Available until `ExitBootServices()` is called. Include: memory allocation, protocol lookup, file I/O, graphics (GOP), network (SNP)
- **Runtime Services**: Survive after `ExitBootServices()`. Include: variable access (GetVariable/SetVariable), time (GetTime), reset, capsule update, monotonic counter
- **GOP (Graphics Output Protocol)**: Replaces VESA/VBE — provides a linear framebuffer at any resolution

### Linux Boot Sequence
```
UEFI (or BIOS)
  → GRUB2 (or systemd-boot)
    → Linux kernel (bzImage: setup.bin + vmlinux.bz2)
      → Decompress and relocate kernel
        → start_kernel() — architecture-independent init
          → rest_init() — spawns init process (PID 1)
            → initramfs (if present) or directly to init on rootfs
              → systemd (PID 1) — service manager
                → Targets: basic.target → multi-user.target → graphical.target
```

**initramfs (Initial RAM Filesystem):**
A cpio archive that the kernel mounts as the initial root filesystem. Contains:
- Essential kernel modules (storage drivers, filesystem drivers)
- Device mapper, LVM, encryption tools (cryptsetup)
- The `/init` script that mounts the real root filesystem
- `switch_root` to pivot from initramfs to real root

Why initramfs? The kernel can't read the root filesystem until the right storage driver is loaded. The initramfs provides those modules.

### ACPI (Advanced Configuration and Power Interface)
ACPI tables are provided by firmware and describe hardware that the OS can't probe:

Key tables:
- **RSDP** (Root System Description Pointer): Entry point — found by scanning memory
- **RSDT/XSDT**: Pointers to all other tables
- **DSDT** (Differentiated System Description Table): AML bytecode describing devices, power states, thermal zones
- **MADT** (Multiple APIC Description Table): CPU topology, IO-APIC configuration
- **MCFG** (PCI Express Memory-mapped Configuration): PCIe ECAM regions
- **FACP** (Fixed ACPI Description Table): Power management registers, reset register
- **SRAT** (System Resource Affinity Table): NUMA topology

The kernel interprets AML bytecode via the ACPICA interpreter to discover devices and manage power. On modern systems, ACPI is the authoritative source for hardware layout — it's not optional.

### Device Tree (ARM/RISC-V)
ARM and RISC-V systems don't have ACPI typically (though ARM servers do). Instead they use **Device Tree** (.dtb files):

```dts
// Example device tree snippet
/ {
    compatible = "myvendor,myboard";
    #address-cells = <1>;
    #size-cells = <1>;

    memory@80000000 {
        device_type = "memory";
        reg = <0x80000000 0x40000000>;  // 1GB at 2GB offset
    };

    uart@101f1000 {
        compatible = "arm,pl011";
        reg = <0x101f1000 0x1000>;
        interrupts = <0 12 4>;
        clock-frequency = <24000000>;
    };
};
```

Device tree is compiled from `.dts` → `.dtb` (binary) and passed to the kernel by the bootloader (U-Boot, typically). It's a static description — unlike ACPI, there's no runtime AML interpretation.

### Writing a UEFI Application
```c
// hello_uefi.c — compile with EDK2 or gnu-efi
#include <efi.h>
#include <efilib.h>

EFI_STATUS
EFI_FUNC
efi_main(EFI_HANDLE ImageHandle, EFI_SYSTEM_TABLE *SystemTable) {
    InitializeLib(ImageHandle, SystemTable);
    
    // Clear screen
    SystemTable->ConOut->ClearScreen(SystemTable->ConOut);
    
    // Print using UEFI services (no printf — no libc in UEFI!)
    Print(L"Hello from UEFI!\n");
    
    // Get memory map
    UINTN mapSize = 0, mapKey, descriptorSize;
    UINT32 descriptorVersion;
    SystemTable->BootServices->GetMemoryMap(
        &mapSize, NULL, &mapKey, &descriptorSize, &descriptorVersion);
    
    EFI_MEMORY_DESCRIPTOR *mmap;
    SystemTable->BootServices->AllocatePool(
        EfiLoaderData, mapSize, (void**)&mmap);
    SystemTable->BootServices->GetMemoryMap(
        &mapSize, mmap, &mapKey, &descriptorSize, &descriptorVersion);
    
    // Exit boot services (kernel would do this before taking over)
    SystemTable->BootServices->ExitBootServices(ImageHandle, mapKey);
    
    // After this point: no more UEFI Boot Services!
    // Only Runtime Services are available.
    
    // Halt
    while (1) __asm__ volatile ("hlt");
    return EFI_SUCCESS;  // Unreachable
}
```

Key differences from normal C:
- No libc — use UEFI-provided functions (`Print`, `AllocatePool`, etc.)
- No `main(int, char**)` — it's `efi_main(EFI_HANDLE, EFI_SYSTEM_TABLE*)`
- WCHAR strings (UCS-2), not char
- MS ABI calling convention on x86_64 (not System V)
- No process model — you're the only thing running in the UEFI environment

USER: Explain device drivers in operating systems. Cover the Linux driver model (platform devices, PCI bus enumeration, device tree bindings), character vs block vs network drivers, interrupt handling in drivers (top half/bottom half, tasklets, workqueues), memory-mapped I/O vs port I/O, and how to write a simple platform driver.
BOT: ## Device Drivers — Deep Dive

### Linux Device Model
The Linux kernel organizes devices into a tree structure under `/sys/devices`. Three key abstractions:

**1. `struct device`**: Represents a physical or virtual device. Has parent pointer, bus type, driver pointer, DMA mask, device tree node (`of_node`).

**2. `struct device_driver`**: Represents a driver that can handle devices. Has `probe()` and `remove()` callbacks, a list of supported device IDs.

**3. `struct bus_type`**: Represents a bus (PCI, USB, I2C, SPI, platform). Has `match()` function to pair devices and drivers.

```
Bus match happens on:
- PCI: vendor ID + device ID from PCI config space
- USB: vendor ID + product ID from USB descriptors
- Platform: compatible string matching from device tree or ACPI
- I2C/SPI: same concept with bus-specific addressing
```

### Platform Devices (Device Tree / ACPI)
For non-discoverable hardware (embedded SoC peripherals, legacy PC devices):

```c
// Driver side:
static const struct of_device_id mydrv_of_match[] = {
    { .compatible = "vendor,mydevice" },
    { }
};
MODULE_DEVICE_TABLE(of, mydrv_of_match);

static int mydrv_probe(struct platform_device *pdev) {
    struct resource *mem = platform_get_resource(pdev, IORESOURCE_MEM, 0);
    void __iomem *base = devm_ioremap_resource(&pdev->dev, mem);
    
    int irq = platform_get_irq(pdev, 0);
    devm_request_irq(&pdev->dev, irq, mydrv_isr, 0, "mydrv", pdev);
    
    // Initialize hardware, register with subsystem...
    return 0;
}

static struct platform_driver mydrv_driver = {
    .probe  = mydrv_probe,
    .remove = mydrv_remove,
    .driver = {
        .name = "mydrv",
        .of_match_table = mydrv_of_match,
    },
};
module_platform_driver(mydrv_driver);
```

Device tree snippet that triggers this:
```dts
mydevice@40000000 {
    compatible = "vendor,mydevice";
    reg = <0x40000000 0x1000>;
    interrupts = <0 42 4>;
};
```

### PCI Bus Enumeration
PCI devices are self-describing (unlike platform devices). Enumeration:

1. **Recursive bus scan**: Start at bus 0, read config space for each device
2. **Read Vendor ID**: If 0xFFFF → no device. Otherwise valid device.
3. **Read Header Type**: If multi-function (bit 7), scan functions 1-7
4. **If PCI-to-PCI bridge** (Header Type 1): Recurse into subordinate bus
5. **Match drivers**: Look up `pci_device_id` table against vendor/device/revision

PCI config space (256 bytes, or 4096 for PCIe extended):
```
Offset  Size  Field
0x00    2     Vendor ID
0x02    2     Device ID
0x04    2     Command (bus master, memory space, I/O space enables)
0x06    2     Status
0x08    1     Revision ID
0x09    3     Class Code (e.g., 0x010000 = SCSI controller)
0x0C    1     Cache Line Size
0x10    24    BAR0-BAR5 (Base Address Registers) — memory or I/O resources
0x34    1     Capabilities Pointer (linked list)
0x3C    1     Interrupt Line (IRQ routed by firmware)
```

### Character vs Block vs Network Drivers

**Character Devices:**
- Stream of bytes, sequential access
- Operations: `open`, `release`, `read`, `write`, `llseek`, `ioctl`, `mmap`
- Registered with `register_chrdev()` or `cdev_add()`
- Examples: `/dev/tty`, `/dev/null`, `/dev/mem`, I2C sensors, GPIO
- Accessed via `read()`/`write()` system calls

**Block Devices:**
- Random access in fixed-size blocks (usually 512 or 4096 bytes)
- Operations: `open`, `release`, `submit_bio` (processes a bio — block I/O)
- Has a request queue for scheduling and merging requests
- Page cache integration — `read()` goes through page cache
- Examples: `sda`, `nvme0n1`, `loop0`
- Registered with `register_blkdev()`, `blk_mq_alloc_tag_set()`, `add_disk()`

**Network Devices:**
- Packet-oriented, no filesystem representation
- Operations: `ndo_open`, `ndo_stop`, `ndo_start_xmit` (transmit), receive via NAPI
- Registered with `register_netdev()`
- NAPI (New API): Interrupt mitigation — on packet arrival, disable RX interrupts and poll in softirq. Re-enable when queue is drained.
- Examples: `eth0`, `wlan0`

### Interrupt Handling: Top Half / Bottom Half

**Top Half (Hard IRQ Handler):**
- Runs immediately when IRQ fires
- Must be FAST — interrupts are disabled on this CPU
- Does minimal work: acknowledge IRQ, copy data, schedule bottom half
- **NEVER sleeps** (no mutex, no memory allocation with GFP_KERNEL, no copy_from_user)

**Bottom Half Mechanisms:**

| Mechanism | Context | Concurrency | Sleep OK? | Use Case |
|-----------|---------|-------------|-----------|----------|
| **Softirq** | Softirq (ksoftirqd) | Same softirq serialized | No | Networking (NET_RX, NET_TX), block layer |
| **Tasklet** | Softirq | Same tasklet serialized | No | Simple deferred work, driver ISR follow-up |
| **Workqueue** | Kernel thread | Full concurrency | Yes | Long-running work, needs mutex/sleep |
| **Threaded IRQ** | Kernel thread | Per-IRQ thread | Yes | Complex I2C/SPI drivers, slow devices |

```c
// Tasklet example (bottom half):
static void my_bottom_half(unsigned long data) {
    struct mydev *dev = (struct mydev *)data;
    // Process data collected in top half
    // Runs in softirq context — still can't sleep
}
DECLARE_TASKLET(my_tasklet, my_bottom_half, (unsigned long)dev);

static irqreturn_t my_isr(int irq, void *data) {
    struct mydev *dev = data;
    // Top half: acknowledge interrupt, save data
    writel(readl(dev->regs + REG_STATUS) | IRQ_ACK, dev->regs + REG_STATUS);
    tasklet_schedule(&dev->tasklet);  // Schedule bottom half
    return IRQ_HANDLED;
}

// Workqueue example (can sleep):
static void my_work_func(struct work_struct *work) {
    struct mydev *dev = container_of(work, struct mydev, work);
    mutex_lock(&dev->lock);
    // Do slow I2C/SPI transactions, allocate memory, etc.
    mutex_unlock(&dev->lock);
}
INIT_WORK(&dev->work, my_work_func);
schedule_work(&dev->work);  // From ISR or tasklet
```

### MMIO vs Port I/O
- **Port I/O (x86 legacy)**: Separate I/O address space. `inb`/`outb` instructions. Used by legacy devices (PIC, PIT, PS/2). Slower.
- **MMIO (Memory-Mapped I/O)**: Device registers mapped into physical memory space. Use regular `readl`/`writel` (or `ioread32`/`iowrite32`). All modern devices (PCIe, ARM peripherals).

```c
// MMIO access patterns:
void __iomem *regs = ioremap(phys_addr, size);
u32 val = readl(regs + REG_OFFSET);       // 32-bit read
writel(val | BIT(3), regs + REG_OFFSET);  // 32-bit write
readl_relaxed(regs + REG_OFFSET);         // No memory barrier (faster)

// Ensure write ordering (critical for device control):
writel(cmd, regs + REG_COMMAND);
wmb();  // Write memory barrier — command is sent before status read
u32 status = readl(regs + REG_STATUS);
```

### Simple Platform Driver — Full Example
```c
// gpio_led.c — Simple GPIO LED driver
#include <linux/module.h>
#include <linux/platform_device.h>
#include <linux/gpio/consumer.h>
#include <linux/of.h>

struct gpio_led {
    struct gpio_desc *gpio;
    int state;
};

static int gpio_led_probe(struct platform_device *pdev) {
    struct gpio_led *led;
    
    led = devm_kzalloc(&pdev->dev, sizeof(*led), GFP_KERNEL);
    if (!led) return -ENOMEM;
    
    // Get GPIO from device tree / ACPI
    led->gpio = devm_gpiod_get(&pdev->dev, NULL, GPIOD_OUT_LOW);
    if (IS_ERR(led->gpio))
        return PTR_ERR(led->gpio);
    
    platform_set_drvdata(pdev, led);
    
    // Expose via sysfs
    device_create_file(&pdev->dev, &dev_attr_led_state);
    
    dev_info(&pdev->dev, "LED driver loaded\n");
    return 0;
}

static int gpio_led_remove(struct platform_device *pdev) {
    dev_info(&pdev->dev, "LED driver removed\n");
    return 0;
}

static const struct of_device_id gpio_led_of_match[] = {
    { .compatible = "myvendor,gpio-led" },
    { }
};
MODULE_DEVICE_TABLE(of, gpio_led_of_match);

static struct platform_driver gpio_led_driver = {
    .probe  = gpio_led_probe,
    .remove = gpio_led_remove,
    .driver = {
        .name = "gpio-led",
        .of_match_table = gpio_led_of_match,
    },
};
module_platform_driver(gpio_led_driver);

MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("Simple GPIO LED Platform Driver");
```

### Driver Development Best Practices
1. **Error handling**: Always check return values. `IS_ERR()`, `PTR_ERR()`, `-ENOMEM`, `-EIO`.
2. **Resource management**: Use `devm_*` variants (devres) — auto-cleanup on probe failure or remove.
3. **Locking rules**: Device lock → never held across `copy_from_user`. rtnl_lock for networking.
4. **Use `pr_debug`/`dev_dbg`**: Enable with `dynamic_debug` instead of leaving `printk` in production.
5. **Power management**: Implement `suspend`/`resume` callbacks. Use `pm_runtime` for runtime PM.
6. **DMA**: Use DMA API (`dma_alloc_coherent`, `dma_map_single`). Never use virt_to_phys on kmalloc'd memory.
7. **Testing**: KUnit for unit tests, `kernelci` for integration, `syzkaller` for fuzzing syscall interfaces.

USER: Explain memory management in an OS kernel at the implementation level. Cover the buddy allocator, slab/SLUB allocator, kmalloc, vmalloc, kmem_cache, page reclaim, OOM killer, and NUMA-aware allocation. Include code-level details.
BOT: ## Kernel Memory Management — Implementation Level

### The Buddy Allocator

The buddy system manages physical pages in power-of-2 blocks. Each free area is tracked in a free_list array indexed by order (0-10 on 4KB pages):

```c
// Simplified buddy allocator (Linux-style)
#define MAX_ORDER 11

struct page {
    unsigned long flags;
    struct list_head lru;     // For free list
    int order;
    // ... refcount, mapping, index, etc.
};

struct free_area {
    struct list_head free_list;
    unsigned long nr_free;
};

struct zone {
    struct free_area free_area[MAX_ORDER];
    spinlock_t lock;
    // ... watermark levels, per-CPU pagesets
};

// Allocation (simplified):
struct page *__rmqueue(struct zone *zone, unsigned int order) {
    struct free_area *area;
    unsigned int current_order;
    
    for (current_order = order; current_order < MAX_ORDER; current_order++) {
        area = &zone->free_area[current_order];
        if (!list_empty(&area->free_list)) {
            struct page *page = list_first_entry(&area->free_list, struct page, lru);
            list_del(&page->lru);
            
            // Split larger blocks into smaller buddies
            while (current_order > order) {
                current_order--;
                area = &zone->free_area[current_order];
                struct page *buddy = page + (1 << current_order);
                buddy->order = current_order;
                list_add(&buddy->lru, &area->free_list);  // Buddy goes to free list
            }
            page->order = order;
            return page;
        }
    }
    return NULL;  // OOM — no memory available
}

// Free:
void __free_pages(struct page *page, unsigned int order) {
    struct zone *zone = page_zone(page);
    unsigned long pfn = page_to_pfn(page);
    
    while (order < MAX_ORDER - 1) {
        // Compute buddy page frame number
        unsigned long buddy_pfn = pfn ^ (1 << order);  // XOR to find buddy
        struct page *buddy = pfn_to_page(buddy_pfn);
        
        // Can we coalesce?
        if (buddy->order != order) break;
        if (page_count(buddy) != 0) break;  // Buddy is in use
        
        // Remove buddy from its free list and merge
        list_del(&buddy->lru);
        order++;
        pfn &= buddy_pfn;  // Use the lower PFN as the combined block
        page = pfn_to_page(pfn);
    }
    
    page->order = order;
    list_add(&page->lru, &zone->free_area[order].free_list);
}
```

### Slab/SLUB Allocator

Slab sits on top of buddy — it carves small objects from pages:

```c
// Creating a cache for frequently-allocated structs:
struct kmem_cache {
    const char *name;
    unsigned int object_size;
    unsigned int align;
    unsigned int flags;
    struct kmem_cache_node *node[MAX_NUMNODES];  // Per-NUMA node
};

// Per-CPU cache for lockless fast path:
struct kmem_cache_cpu {
    void **freelist;     // Points to next free object (already initialized)
    struct page *page;   // Current slab page
    unsigned int tid;    // Transaction ID for lock-free access
};

// Allocation fast path (SLUB):
static __always_inline void *slab_alloc(struct kmem_cache *s, gfp_t flags) {
    void *object;
    struct kmem_cache_cpu *c;
    unsigned long tid;
    
    local_irq_save();
    c = this_cpu_ptr(s->cpu_slab);
    tid = c->tid;
    
    object = c->freelist;
    if (unlikely(!object)) {
        // Slow path: need to get a new slab from partial list or buddy
        object = __slab_alloc(s, flags);
        goto out;
    }
    
    c->freelist = *(void **)object;  // Next free object pointer is stored in the freed slot
    c->tid = next_tid(tid);
out:
    local_irq_restore();
    return object;
}

// The freelist is a singly-linked list embedded in freed objects:
// Each freed object stores a pointer to the next free object at offset 0
// No external metadata needed — the pointer lives in the memory being managed
```

### kmalloc — General-Purpose Kernel Allocation

```c
// kmalloc uses slab under the hood — it maps sizes to pre-created caches:
// kmalloc-8, kmalloc-16, kmalloc-32, ... kmalloc-8192

void *kmalloc(size_t size, gfp_t flags) {
    struct kmem_cache *cachep;
    
    if (size > KMALLOC_MAX_CACHE_SIZE) {
        // Fall back to page allocator for large allocations
        return kmalloc_large(size, flags);
    }
    
    // Find the correct size cache
    int index = kmalloc_index(size);  // Rounds up to next power-of-2 cache
    cachep = kmalloc_caches[index];
    
    return kmem_cache_alloc(cachep, flags);
}
```

### GFP Flags (Get Free Pages)

The `gfp_t` flags control allocation behavior:

```c
// Context flags:
GFP_KERNEL     // Can sleep, can reclaim pages, can trigger OOM. DEFAULT for kernel code.
GFP_ATOMIC     // Cannot sleep, minimal reclaim. Use in ISR, spinlock, softirq context.
GFP_NOWAIT     // No sleeping, no reclaim. Returns NULL if no memory immediately.

// Modifier flags:
__GFP_HIGH     // High priority — can use emergency reserves
__GFP_IO       // Can start filesystem I/O for reclaim
__GFP_FS       // Can call filesystem operations for reclaim
__GFP_RECLAIM  // Can do direct reclaim
__GFP_NOFAIL   // Loop until allocation succeeds (dangerous — use only for tiny allocs)
__GFP_NORETRY  // No retry on failure — fail fast
__GFP_ZERO     // Zero the allocated memory
__GFP_DMA      // Allocate from ZONE_DMA (below 16MB — for ISA devices)
__GFP_DMA32    // Allocate from ZONE_DMA32 (below 4GB — for 32-bit PCI devices)

// Common combinations:
GFP_KERNEL  = __GFP_RECLAIM | __GFP_IO | __GFP_FS     // "I can sleep, do what you need"
GFP_ATOMIC  = __GFP_HIGH                               // "I'm in ISR, give me emergency reserves"
GFP_USER    = GFP_KERNEL | __GFP_HARDWALL             // For user-space allocations (cgroup aware)
```

### vmalloc — Non-Contiguous Physical, Contiguous Virtual

```c
// kmalloc: contiguous in physical memory (good for DMA)
// vmalloc: contiguous in virtual space, scattered physical pages

void *vmalloc(unsigned long size) {
    // 1. Allocate virtual address range (find hole in vmalloc area)
    struct vm_struct *area = get_vm_area(size, VM_ALLOC);
    
    // 2. Allocate individual physical pages (no contiguity required)
    struct page **pages = kmalloc(nr_pages * sizeof(struct page *), GFP_KERNEL);
    for (int i = 0; i < nr_pages; i++) {
        pages[i] = alloc_page(GFP_KERNEL);  // Page from buddy — anywhere in RAM
    }
    
    // 3. Map each physical page into the virtual range via page tables
    map_vm_area(area, PAGE_KERNEL, pages);
    
    return area->addr;
}
```

Use `vmalloc` for large kernel buffers (modules, swap structures) that don't need DMA. It avoids the fragmentation problem of `kmalloc` for large sizes.

### Page Reclaim and the LRU

When memory is low, the kernel reclaims pages:

```c
// struct page flags controlling reclaim:
PG_lru       // Page is on LRU list (inactive or active)
PG_referenced  // Page was accessed (moves between active/inactive)
PG_active    // Page is on active LRU (frequently used)
PG_dirty     // Page has been modified — must be written back
PG_writeback // Page is currently being written to disk
PG_swapbacked // Page is backed by swap (anonymous memory)
```

**Two-list LRU (active/inactive):**
```
New page → inactive list
    ↓ (referenced)
Active list (frequently used)
    ↓ (not referenced for a while)
Back to inactive list
    ↓ (still not referenced)
Reclaim candidate (evict or swap)
```

Reclaim order:
1. **Clean page cache pages**: Just drop them (can be re-read from disk)
2. **Dirty page cache pages**: Writeback to disk, then drop
3. **Anonymous pages (heap, stack)**: Swap out to swap device
4. **Kernel reclaim**: Shrink slab caches (drop unused dentries, inodes)

### OOM Killer

When all reclaim fails, the Out-Of-Memory killer selects a process to kill:

```c
// oom_badness() — who gets the axe?
unsigned long oom_badness(struct task_struct *p) {
    unsigned long points = 0;
    
    // Base score: total virtual memory
    points = get_mm_rss(p->mm) + get_mm_counter(p->mm, MM_SWAPENTS) +
             mm_nr_ptes(p->mm) + mm_nr_pmds(p->mm);
    
    // Root processes get a 3% discount (less likely to be killed)
    if (has_capability_noaudit(p, CAP_SYS_ADMIN))
        points -= (points * 3) / 100;
    
    // Adjust for oom_score_adj (user-configured override)
    points += p->signal->oom_score_adj;
    
    return points > 0 ? points : 1;  // Never return 0
}
```

### NUMA-Aware Allocation

On multi-socket systems, memory is divided into nodes:

```c
// Allocate on specific node:
struct page *alloc_pages_node(int nid, gfp_t gfp, unsigned int order);

// Policy functions — where to allocate next:
// MPOL_DEFAULT:     Current node
// MPOL_BIND:        Only from specified nodes (strict)
// MPOL_INTERLEAVE:  Round-robin across nodes (spread bandwidth)
// MPOL_PREFERRED:   Prefer a node, fall back to others

// Automatic NUMA balancing:
// Kernel periodically unmaps pages, and on next access fault, 
// migrates the page to the accessing CPU's node
// Controlled by /proc/sys/kernel/numa_balancing
```

### Memory Zones (x86_64)
```
ZONE_DMA      0-16MB     ISA devices, floppy controllers
ZONE_DMA32    16MB-4GB   32-bit PCI devices
ZONE_NORMAL   4GB-...    Directly mapped kernel memory (lowmem)
ZONE_MOVABLE  ...        Migratable pages (defragmentation, hotplug)
```

On x86_64, `ZONE_NORMAL` typically extends to 64TB (the direct map limit). ARM32 has `ZONE_HIGHMEM` for memory above the kernel's virtual address limit — a major pain point that x86_64 doesn't have.

### Common Memory Bugs in Kernel Code
1. **Use-after-free**: Free a kmalloc'd buffer, then access it. KASAN (Kernel Address Sanitizer) catches this.
2. **Double free**: Free the same pointer twice. SLUB debug detects redzone corruption.
3. **Memory leak**: Allocate and never free. `kmemleak` scans for unreferenced allocations.
4. **Stack overflow**: Too-large local variables. Kernel stack is only 16KB (or 8KB on 32-bit).
5. **Sleeping in atomic context**: `might_sleep()` debug check in `GFP_KERNEL` allocations when preempt_count != 0.

USER: Explain the networking stack in an OS kernel. Cover the socket layer, TCP/IP implementation, netfilter/iptables, NAPI and interrupt mitigation, zero-copy networking, and how to write a simple network driver.
BOT: ## Kernel Networking Stack — Deep Dive

### The Socket Layer
The socket is the user-space interface to the networking stack. Internally:

```c
// struct socket (VFS-level) vs struct sock (protocol-level)
struct socket {
    socket_state    state;
    short           type;       // SOCK_STREAM, SOCK_DGRAM, SOCK_RAW
    unsigned long   flags;
    struct file     *file;
    struct sock     *sk;        // Protocol-specific socket
    const struct proto_ops *ops; // Operations table
};

// Protocol operations (dispatch table):
struct proto_ops {
    int     (*bind)(struct socket *sock, struct sockaddr *addr, int addr_len);
    int     (*connect)(struct socket *sock, struct sockaddr *addr, int addr_len, int flags);
    int     (*accept)(struct socket *sock, struct socket *newsock, int flags);
    int     (*listen)(struct socket *sock, int backlog);
    int     (*sendmsg)(struct socket *sock, struct msghdr *msg, size_t len);
    int     (*recvmsg)(struct socket *sock, struct msghdr *msg, size_t len, int flags);
    // ...
};
```

### TCP Implementation — Key Data Structures

```c
// The TCP control block (simplified):
struct tcp_sock {
    struct inet_connection_sock inet_conn;
    
    // Sequence numbers
    u32 snd_una;        // Oldest unacknowledged sequence number
    u32 snd_nxt;        // Next sequence number to send
    u32 snd_wnd;        // Send window (receiver's advertised window)
    u32 rcv_nxt;        // Next expected receive sequence number
    u32 rcv_wnd;        // Receive window (our buffer space)
    
    // Congestion control
    u32 snd_cwnd;       // Congestion window (packets in flight)
    u32 snd_ssthresh;   // Slow start threshold
    u32 mss_cache;      // Maximum segment size
    
    // Retransmission
    u32 retransmit_high; // Highest sequence number retransmitted
    u32 lost_out;        // Lost packets counter
    u32 retrans_out;     // Retransmitted packets counter
    
    // Timers
    u32 rto;            // Retransmission timeout (computed from RTT)
    u32 srtt_us;        // Smoothed round-trip time
    u32 mdev_us;        // Mean deviation of RTT
};
```

**TCP State Machine (the well-known diagram):**
```
CLOSED → LISTEN → SYN_RCVD → ESTABLISHED → FIN_WAIT1 → FIN_WAIT2 → TIME_WAIT → CLOSED
                                               ↓              ↓
                                          CLOSE_WAIT      CLOSING
                                               ↓              ↓
                                           LAST_ACK       (direct)
```

**TCP Congestion Control Algorithms in Linux:**
- **Reno**: Classic AIMD (Additive Increase Multiplicative Decrease). Halves cwnd on loss.
- **CUBIC** (default since 2.6.19): Uses a cubic function for window growth — faster recovery after loss, better for high-BDP links.
- **BBR** (Bottleneck Bandwidth and RRT, Google): Model-based — measures available bandwidth and RTT rather than using loss as a signal.
- **NewReno, Vegas, Westwood, H-TCP**: Each optimized for different link characteristics (wireless, satellite, datacenter).

### The sk_buff (Socket Buffer)
The universal packet container in the Linux networking stack:

```c
struct sk_buff {
    // Data pointers
    unsigned char    *head;      // Start of allocated buffer
    unsigned char    *data;      // Start of current protocol data
    unsigned char    *tail;      // End of current protocol data
    unsigned char    *end;       // End of allocated buffer
    
    // Each layer reserves headroom and pushes headers:
    // head → [L2 hdr][L3 hdr][L4 hdr][payload] ← data
    //          tail (advances as headers are removed)
    
    struct sock      *sk;        // Owner socket
    ktime_t          tstamp;    // Packet timestamp
    struct net_device *dev;      // Network device
    unsigned int     len;        // Total packet length
    unsigned int     data_len;   // Fragmented data length
    __u16            protocol;   // Ethertype (ETH_P_IP, ETH_P_ARP, ...)
    
    // For segmentation offload:
    unsigned int     gso_size;   // Generic segmentation offload size
    unsigned int     gso_segs;   // Number of segments
    
    // Shared info for fragments (scatter/gather I/O)
    struct skb_shared_info {
        unsigned short  nr_frags;
        skb_frag_t      frags[MAX_SKB_FRAGS];  // Page fragments
    };
};
```

### NAPI — Interrupt Mitigation
Without NAPI: every packet triggers an IRQ → high CPU usage under load ("interrupt storm").

With NAPI:
1. Packet arrives → IRQ fires → ISR disables RX interrupts and schedules NAPI poll
2. Softirq runs `net_rx_action()` → calls driver's `poll()` in a loop
3. `poll()` processes up to `budget` (default 64) packets from the RX ring
4. If more packets remain, re-schedule poll. If ring is empty, re-enable interrupts.

```c
// NAPI poll callback (simplified):
int my_driver_poll(struct napi_struct *napi, int budget) {
    int packets_processed = 0;
    
    while (packets_processed < budget) {
        struct sk_buff *skb;
        skb = rx_ring_pop();    // Get next packet from hardware ring
        if (!skb) break;
        
        skb->protocol = eth_type_trans(skb, netdev);
        netif_receive_skb(skb); // Pass up to IP stack
        packets_processed++;
    }
    
    if (packets_processed < budget) {
        napi_complete_done(napi, packets_processed);
        enable_rx_interrupts(); // Re-enable IRQs — queue is drained
    }
    
    return packets_processed;
}
```

### netfilter / iptables
Netfilter provides hook points at five locations in the packet flow:

```
PREROUTING → [routing decision] → FORWARD → POSTROUTING
                  ↓
              [local process]
                  ↓
               INPUT → [socket] → OUTPUT → POSTROUTING
```

Each hook can register callback functions (iptables rules). Rules traverse tables:
- **filter**: INPUT, FORWARD, OUTPUT — accept/drop/reject
- **nat**: PREROUTING (DNAT), POSTROUTING (SNAT), OUTPUT
- **mangle**: All hooks — packet modification (TOS, TTL, MARK)

### Zero-Copy Networking
Traditional path copies data twice: kernel buffer → user buffer. Zero-copy avoids these copies:

**sendfile()**: Data goes directly from page cache to socket buffer:
```c
// Without sendfile: read() → user buffer → write() → kernel buffer = 2 copies
// With sendfile: page cache → DMA to NIC = 0 CPU copies
sendfile(sockfd, filefd, NULL, size);
```

**splice()**: Splice data between two file descriptors without userspace:
```c
// Splice a socket to a pipe, then pipe to another socket (proxy pattern)
splice(client_fd, NULL, pipefd[1], NULL, size, SPLICE_F_MOVE);
splice(pipefd[0], NULL, server_fd, NULL, size, SPLICE_F_MOVE);
```

**io_uring**: Shared ring buffers between kernel and userspace — no copy at all for registered buffers. Submitted and completed I/O operations communicated via lockless ring buffers.

### Writing a Simple Network Driver

```c
#include <linux/netdevice.h>
#include <linux/etherdevice.h>

struct my_netdev_priv {
    void __iomem *regs;
    struct napi_struct napi;
    int irq;
};

static int my_netdev_open(struct net_device *dev) {
    struct my_netdev_priv *priv = netdev_priv(dev);
    napi_enable(&priv->napi);
    enable_irq(priv->irq);
    netif_start_queue(dev);  // Allow upper layers to queue packets
    return 0;
}

static netdev_tx_t my_netdev_xmit(struct sk_buff *skb, struct net_device *dev) {
    struct my_netdev_priv *priv = netdev_priv(dev);
    
    // 1. Map skb data for DMA
    dma_addr_t dma = dma_map_single(dev->dev.parent, skb->data, 
                                     skb->len, DMA_TO_DEVICE);
    
    // 2. Write descriptor to hardware TX ring
    tx_ring[tx_head].addr = dma;
    tx_ring[tx_head].len = skb->len;
    tx_ring[tx_head].flags = TX_DESC_EOP | TX_DESC_OWN;  // Owned by HW
    wmb();
    writel(tx_head, priv->regs + REG_TX_TAIL);
    
    // 3. Track skb for later cleanup in TX completion
    dev_kfree_skb_any(skb);  // Free after DMA completes
    return NETDEV_TX_OK;
}

static struct net_device_ops my_netdev_ops = {
    .ndo_open = my_netdev_open,
    .ndo_start_xmit = my_netdev_xmit,
    .ndo_set_mac_address = eth_mac_addr,
};

// Register:
struct net_device *dev = alloc_etherdev(sizeof(struct my_netdev_priv));
dev->netdev_ops = &my_netdev_ops;
register_netdev(dev);
```

USER: Explain OS security mechanisms in depth. Cover kernel ASLR (KASLR), user-space ASLR, stack canaries, NX/DEP, SMEP/SMAP, KPTI, seccomp BPF, Secure Boot, capabilities, SELinux/AppArmor, and common kernel exploitation techniques with their mitigations.
BOT: ## OS Security — Deep Dive

### Address Space Layout Randomization (ASLR)

**User-space ASLR:**
Randomizes the base addresses of the stack, heap, mmap region, and executable. Without ASLR, an attacker knows exactly where their shellcode will land.

```c
// Typical user-space layout (addresses vary per-execution):
// 0x7fff??????        Stack (randomized by 2^22 offsets on x86_64)
// 0x7f????????        mmap region (shared libraries, anonymous mappings)
// 0x55????????        PIE executable base
// 0x??????????        Heap (after brk, randomized by arch_randomize_brk)
```

**KASLR (Kernel ASLR):**
Randomizes the kernel's base virtual address at boot. Without KASLR, every kernel symbol has a known address:

```
Without KASLR: kernel at 0xffffffff81000000 (known)
With KASLR:    kernel at 0xffffffff81000000 + random_offset (unknown)
               random_offset is 0-1GB on x86_64 (up to 2^30)
```

KASLR is defeated if an attacker can leak a single kernel pointer (info leak). Any `printk` of a `%p` pointer exposes the offset. That's why Linux 4.15+ restricts `%p` to hashed values unless `%px` is used.

### Stack Canaries (SSP — Stack Smashing Protector)

A random value placed between local variables and the return address on the stack:

```c
// Without canary:
// [local buf][return addr][saved rbp]  ← overflow buf → overwrite return addr

// With canary (-fstack-protector, enabled by default in kernel):
// GCC generates:
void function(void) {
    unsigned long canary = __stack_chk_guard;  // Global random value
    // [canary][local buf][return addr][saved rbp]
    // ... function body ...
    if (canary != __stack_chk_guard)
        __stack_chk_fail();  // panic — stack smashing detected!
}

// In Linux kernel, __stack_chk_guard is per-CPU and initialized from RDRAND:
// arch/x86/include/asm/stackprotector.h
static inline void load_stack_canary_segment(void) {
    get_random_bytes(&canary, sizeof(canary));
    this_cpu_write(__stack_chk_guard, canary);
}
```

Bypasses: Canaries don't protect against format string attacks (they overwrite pointers, not the stack linearly) or data-only attacks. They're a defense-in-depth measure, not a silver bullet.

### NX/DEP (No-eXecute / Data Execution Prevention)

Marks memory pages as non-executable via the NX bit in page table entries (bit 63 on x86_64). Stack and heap are NX by default:

```
PTE: | NX(63) | ... | Present(0) | R/W(1) | User(2) | ... |

W^X policy: A page is either Writable OR eXecutable — never both.
```

This prevents classic shellcode injection. The attacker's code on the stack won't execute — the CPU throws a page fault (#PF with reserved bit set) on instruction fetch.

Bypass: **ROP (Return-Oriented Programming)**. Instead of injecting code, chain together existing code sequences ("gadgets") that end with `ret`. Each gadget does a small operation (pop a register, write to memory), then returns to the next gadget via a forged stack.

### SMEP and SMAP (x86_64)

**SMEP (Supervisor Mode Execution Prevention):**
The kernel cannot execute code from user-space pages. Controlled by CR4.SMEP (bit 20). Set at boot:

```c
// In the kernel:
cr4_set_bits(X86_CR4_SMEP);
```

Without SMEP: an attacker can map shellcode in user space, then redirect the kernel to execute it (kernel can access user memory by default). SMEP blocks this — any jump to a user address while in ring 0 triggers a page fault.

**SMAP (Supervisor Mode Access Prevention):**
The kernel cannot read/write user-space memory. Controlled by CR4.SMAP (bit 21). When enabled, kernel code must use `stac` (Set AC flag) before accessing user memory and `clac` (Clear AC flag) after:

```asm
stac            ; Allow user memory access
mov rax, [rdi]  ; Read from user buffer (rdi = userspace pointer)
clac            ; Disallow user memory access
```

The `copy_from_user()` / `copy_to_user()` functions handle stac/clac automatically. SMAP prevents the kernel from accidentally dereferencing user-controlled pointers — a common bug pattern.

### KPTI (Kernel Page Table Isolation)

Originally for Meltdown mitigation (CPU bug leaking kernel memory via speculative execution). Two sets of page tables per process:

- **User page tables**: Map only the bare minimum kernel code (entry/exit trampoline, VDSO) + user space. This is what's active when running in user mode.
- **Kernel page tables**: Full kernel mapping + user space. Only active when actually in kernel mode (after syscall/exception entry).

The switch happens in the entry/exit trampoline. Cost: TLB flush on every syscall → 5-30% overhead on syscall-heavy workloads. PCID (Process Context Identifiers) mitigates this by tagging TLB entries so they don't need to be fully flushed.

### seccomp (Secure Computing)

Restricts the syscalls a process can make. Two modes:

**seccomp strict (mode 1):**
```c
prctl(PR_SET_SECCOMP, SECCOMP_MODE_STRICT);
// Only allowed: read(2), write(2), _exit(2), sigreturn(2)
// Any other syscall → SIGKILL
```

**seccomp-bpf (mode 2):**
```c
#include <linux/seccomp.h>
#include <linux/filter.h>

// BPF program that kills process if it tries to use ptrace:
struct sock_filter filter[] = {
    BPF_STMT(BPF_LD | BPF_W | BPF_ABS, offsetof(struct seccomp_data, nr)),
    BPF_JUMP(BPF_JMP | BPF_JEQ | BPF_K, __NR_ptrace, 1, 0),
    BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_ALLOW),
    BPF_STMT(BPF_RET | BPF_K, SECCOMP_RET_KILL),
};
struct sock_fprog prog = { .len = ARRAY_SIZE(filter), .filter = filter };
prctl(PR_SET_SECCOMP, SECCOMP_MODE_FILTER, &prog);
```

Chrome uses this heavily — renderer processes are locked down to a whitelist of ~50 syscalls. This limits the impact of V8 engine exploits.

### Capabilities

Split root's power into discrete capabilities:
```c
// Instead of running as root, a process gets specific capabilities:
CAP_NET_BIND_SERVICE  // Bind to ports < 1024 (no full root needed!)
CAP_SYS_RAWIO         // Access /dev/mem, iopl, ioperm
CAP_SYS_PTRACE        // ptrace any process
CAP_SYS_ADMIN         // A grab-bag (mount, swapon, sethostname, ...)
CAP_NET_ADMIN         // Network configuration (ifconfig, iptables, routing)
CAP_SYS_MODULE        // Load/unload kernel modules
// ... ~40 capabilities total

// Set on a binary:
// # setcap cap_net_bind_service=+ep /usr/bin/my_server
```

### SELinux / AppArmor (MAC — Mandatory Access Control)

DAC (Discretionary Access Control) = owner decides. MAC = system policy decides, owner can't override.

**SELinux:** Label-based. Every subject (process) and object (file, socket, device) has a security context:
```
system_u:object_r:httpd_sys_content_t:s0   ← file label
system_u:system_r:httpd_t:s0                ← process label

Policy: allow httpd_t httpd_sys_content_t:file { read getattr open };
→ Apache processes can read files labeled httpd_sys_content_t
```

**AppArmor:** Path-based (simpler than SELinux):
```
/usr/sbin/nginx {
    /var/www/** r,       # Read web root
    /var/log/nginx/* w,  # Write logs
    /etc/nginx/** r,     # Read config
    capability net_bind_service,
    # Everything else denied
}
```

### Common Kernel Exploitation Techniques

**1. NULL Pointer Dereference:**
```c
// Kernel bug:
void vulnerable_ioctl(struct file *filp, unsigned int cmd, unsigned long arg) {
    // If ops is NULL (e.g., device not fully initialized):
    filp->f_op->unlocked_ioctl(filp, cmd, arg);  // BUG
}
```
Mitigation: `mmap_min_addr` — can't mmap at address 0. CONFIG_DEFAULT_MMAP_MIN_ADDR=65536.

**2. Use-After-Free:**
```c
// Thread A frees a struct, Thread B uses it:
kfree(obj);        // A: free
// ... timer or race window ...
obj->callback();   // B: use-after-free → code execution via function pointer overwrite
```
Mitigation: KASAN (detection), CONFIG_SLAB_FREELIST_HARDENED (poisons freed objects), freelist randomization.

**3. Double Fetch:**
```c
// Attacker's thread modifies user buffer between kernel's checks:
if (copy_from_user(&len, user_ptr, sizeof(len))) return -EFAULT;
if (len > MAX_SIZE) return -EINVAL;     // Check
// ... attacker changes *user_ptr here ...
buf = kmalloc(len, GFP_KERNEL);         // Use: different value!
```
Mitigation: `copy_from_user()` once into a kernel variable, use only that copy.

**4. Spectre/Meltdown (CPU bugs):**
- **Spectre v1**: Bounds check bypass through branch prediction training
- **Spectre v2**: Branch target injection
- **Meltdown**: Speculative fetch across kernel/user page table boundary
- Mitigations: `lfence` barriers, retpoline (spectre v2), KPTI (meltdown)

### Secure Boot

UEFI Secure Boot ensures only cryptographically signed code runs during boot:

1. Platform Key (PK): Owned by OEM/owner. Signs KEK.
2. Key Exchange Key (KEK): Signs the db/dbx databases.
3. Allowed DB (db): Hashes and certificates of allowed bootloaders/kernels.
4. Disallowed DB (dbx): Blocklisted hashes.

Each stage verifies the signature of the next stage before executing it:
```
UEFI firmware → verifies bootloader (shim) → verifies GRUB → verifies kernel → kernel verifies modules (if MODULE_SIG_FORCE)
```

Lockdown mode (kernel `lockdown=` parameter): Even root can't modify kernel memory when Secure Boot is active. `/dev/mem` restricted, `kexec` blocked, BPF restricted, hibernation disabled.

USER: Explain kernel debugging and profiling techniques. Cover GDB/kgdb, JTAG hardware debugging, printk and dynamic debug, ftrace, perf, eBPF/bpftrace, KASAN/UBSAN/KMSAN, lockdep, and kernel crash dump analysis (kdump/crash).
BOT: ## Kernel Debugging — Deep Dive

### printk — The Kernel's printf

```c
// printk log levels (include/linux/kern_levels.h):
#define KERN_EMERG   "<0>"  // System is unusable
#define KERN_ALERT   "<1>"  // Action must be taken immediately
#define KERN_CRIT    "<2>"  // Critical conditions
#define KERN_ERR     "<3>"  // Error conditions
#define KERN_WARNING "<4>"  // Warning conditions
#define KERN_NOTICE  "<5>"  // Normal but significant
#define KERN_INFO    "<6>"  // Informational
#define KERN_DEBUG   "<7>"  // Debug-level messages

// Usage:
printk(KERN_ERR "my_driver: unexpected register value 0x%x\n", val);

// pr_* wrappers are preferred (they include function prefix automatically):
pr_emerg("System down!\n");
pr_alert("Immediate action needed\n");
pr_crit("Critical condition\n");
pr_err("Error: %d\n", -EIO);
pr_warn("Warning: deprecated\n");
pr_info("Driver loaded\n");
pr_debug("Reg[0x%x] = 0x%x\n", offset, val);  // Only shown with dynamic_debug
```

**Dynamic Debug:** Enable `pr_debug`/`dev_dbg` at runtime without recompiling:
```bash
# Enable all debug in usb driver:
echo 'module usbcore +p' > /sys/kernel/debug/dynamic_debug/control

# Enable a specific file:
echo 'file drivers/net/ethernet/intel/e1000e/netdev.c +p' > /sys/kernel/debug/dynamic_debug/control

# Enable a specific function with line number:
echo 'func e1000_clean_rx_irq +p' > /sys/kernel/debug/dynamic_debug/control
```

### kgdb — Kernel GDB Stub

Allow GDB to debug the running kernel via serial port or USB:

```bash
# Boot with kgdbwait — kernel stops and waits for debugger:
# kernel command line: kgdboc=ttyS0,115200 kgdbwait

# On debug host:
gdb vmlinux
(gdb) target remote /dev/ttyS0
(gdb) break do_sys_open
(gdb) continue

# Now the kernel breaks when any process calls open()
(gdb) bt
(gdb) info registers
(gdb) print *task
```

kgdb stops ALL CPUs via IPI when the debugger attaches. Limitations:
- Cannot debug interrupt context easily (other CPUs are stopped in an IPI handler)
- Serial port may be shared with console output subsystem
- Very slow if stepping through code one instruction at a time
- Cannot single-step through atomic regions (interrupts disabled, spinlocks held)

### JTAG/SWD Hardware Debugging

For embedded and early-boot debugging where software debuggers can't help:

**JTAG (Joint Test Action Group):** IEEE 1149.1 standard for boundary scan and debug. Gives you:
- Hardware breakpoints (up to 4-8 on ARM)
- Single-stepping through boot code
- Memory read/write even when kernel is crashed
- Register inspection at any point
- Flash programming

**OpenOCD + GDB workflow:**
```bash
# Start OpenOCD with target config:
openocd -f interface/ftdi/jtagkey.cfg -f target/stm32f4x.cfg

# Connect GDB:
arm-none-eabi-gdb kernel.elf
(gdb) target remote localhost:3333
(gdb) monitor reset halt    # Hardware reset, stop at first instruction
(gdb) break _start
(gdb) continue
```

### ftrace — Function Tracer

Built into the kernel, near-zero overhead when not tracing:

```bash
# Available tracers:
cat /sys/kernel/debug/tracing/available_tracers
# function_graph function nop blk mmiotrace

# Trace all function calls:
echo function > /sys/kernel/debug/tracing/current_tracer
echo 1 > /sys/kernel/debug/tracing/tracing_on
cat /sys/kernel/debug/tracing/trace
# Shows every function call with timestamps:
# <idle>-0     [000] d... 1234.567: __schedule <-schedule

# Trace specific functions:
echo do_page_fault > /sys/kernel/debug/tracing/set_ftrace_filter
echo function_graph > /sys/kernel/debug/tracing/current_tracer
# Shows call graph:
# do_page_fault() {
#   __do_page_fault() {
#     handle_mm_fault() {
#       __handle_mm_fault() {
#         handle_pte_fault() {
#           do_anonymous_page() {
#           }
#         }
#       }
#     }
#   }
# }

# Trace a specific process:
echo 1234 > /sys/kernel/debug/tracing/set_ftrace_pid
```

### perf — Performance Counters

Uses hardware PMU (Performance Monitoring Unit) counters:
```bash
# Profile CPU usage (sampling):
perf record -a -g sleep 10      # Record all CPUs for 10s
perf report                      # Flame graph-like output

# Count specific events:
perf stat -e cycles,instructions,cache-misses,page-faults ./my_program

# Live function tracing:
perf top -g

# Trace syscalls:
perf trace -p $(pidof mydaemon)

# Probe a kernel function:
perf probe --add='tcp_sendmsg size=%dx'
perf record -e probe:tcp_sendmsg -aR sleep 10
```

### eBPF / bpftrace

Dynamic, safe kernel tracing with eBPF (extended Berkeley Packet Filter):

```bash
# Count syscalls per-second by process:
bpftrace -e 'tracepoint:raw_syscalls:sys_enter { @[comm] = count(); }'

# Histogram of read() sizes:
bpftrace -e 'tracepoint:syscalls:sys_enter_read { @bytes = hist(args->count); }'

# Trace when a process opens a file:
bpftrace -e 'tracepoint:syscalls:sys_enter_openat {
    printf("%s opened %s\n", comm, str(args->filename));
}'

# Profile kernel stack traces for block I/O:
bpftrace -e 'kprobe:submit_bio { @[kstack] = count(); }'

# One-liner to see what's causing latency on a CPU:
bpftrace -e 'kprobe:finish_task_switch { @runq_lat = hist(nsecs - start); }'
```

eBPF programs are verified by the kernel's in-kernel verifier before execution — they're guaranteed to terminate, never crash, and never access invalid memory. This makes them safe to run in production.

### Kernel Sanitizers

**KASAN (Kernel Address Sanitizer):**
Detects use-after-free and out-of-bounds accesses. Instruments every memory access with shadow memory checking. Overhead: 2-3x slowdown, 1/8th memory for shadow. For development builds only.

```c
// Without KASAN:
int *p = kmalloc(sizeof(*p), GFP_KERNEL);
kfree(p);
*p = 42;  // Silent use-after-free — might work, might corrupt something

// With KASAN:
*p = 42;  // KASAN: use-after-free in my_function+0x42/0x100
          // Read of size 4 at addr ffff880001234000 by task myapp/1234
          // Freed by my_function+0x20/0x100
```

**UBSAN (Undefined Behavior Sanitizer):**
Catches: integer overflow, shift out of bounds, null pointer dereference, alignment violations, signed overflow:

```c
int x = INT_MAX;
x++;  // UBSAN: signed integer overflow: 2147483647 + 1
```

**KMSAN (Kernel Memory Sanitizer):**
Detects use of uninitialized memory. Uses shadow memory (poison bits) tracking. All memory starts as "uninitialized" — only cleared when explicitly initialized.

**KCSAN (Kernel Concurrency Sanitizer):**
Finds data races by observing memory accesses and checking lock ordering:
```
KCSAN: data-race in my_read / my_write:
  read at 0xffff... of 4 bytes by task 1234 on cpu 1:
    my_read+0x42/0x100
  write at 0xffff... of 4 bytes by task 5678 on cpu 3:
    my_write+0x20/0x80
```

### lockdep — Lock Dependency Checker

Proves at runtime that the system's locking order is deadlock-free. Tracks:
- Lock classes (types of locks)
- Lock ordering (which lock was taken first)
- Lock state (held, not held)
- Interrupt state (IRQs enabled, disabled)

```c
// lockdep detects this deadlock:
void thread_A(void) {
    spin_lock(&lock1);
    spin_lock(&lock2);  // lockdep: possible circular locking dependency!
    // A: lock1 → lock2
}

void thread_B(void) {
    spin_lock(&lock2);
    spin_lock(&lock1);  // lockdep: inconsistent lock ordering!
    // B: lock2 → lock1  ← potential deadlock with A
}

// lockdep reports:
// ======================================================
// WARNING: possible circular locking dependency detected
// 5.10.0 #1 Not tainted
// ------------------------------------------------------
// thread_A/1234 is trying to acquire lock:
//  (&lock2){+.+.}-{3:3}, at: thread_A+0x42/0x100
//
// but task is already holding lock:
//  (&lock1){+.+.}-{3:3}, at: thread_A+0x20/0x100
//
// which lock already depends on the new lock.
// ...
// other info that might help us debug this:
//  Possible unsafe locking scenario:
//        CPU0                    CPU1
//        ----                    ----
//   lock(&lock1);
//                                lock(&lock2);
//                                lock(&lock1);
//   lock(&lock2);
//  *** DEADLOCK ***
```

### kdump / crash — Kernel Crash Analysis

When the kernel panics, kdump boots a second ("capture") kernel that saves the crashed kernel's memory to `/var/crash/vmcore`:

```bash
# Analyze with crash tool:
crash /usr/lib/debug/lib/modules/$(uname -r)/vmlinux vmcore

crash> bt          # Backtrace of the crashing CPU
crash> log         # Kernel log buffer (dmesg) at time of crash
crash> ps          # Process list including kernel threads
crash> files 1234  # Open files for PID 1234
crash> kmem -i     # Memory usage information
crash> mod -S      # Loaded modules with addresses

# The bt output tells you EXACTLY what sequence led to the panic:
crash> bt
PID: 1234   TASK: ffff88007c123080  CPU: 2   COMMAND: "myprog"
 #0 [ffff88007c123b38] machine_kexec at ffffffff8104f912
 #1 [ffff88007c123b98] __crash_kexec at ffffffff81124534
 #2 [ffff88007c123c60] panic at ffffffff81687634
 #3 [ffff88007c123ce0] do_page_fault at ffffffff81684230
 #4 [ffff88007c123d70] page_fault at ffffffff816844e6
     RIP: ffffffffa0012340  RSP: ffff88007c123e28
 #5 [ffff88007c123ee0] my_driver_ioctl+0x40/0x80 [mydriver]  ← CRASH HERE
```

### Debugging Workflow Summary

| Phase | Tool | What It Catches |
|-------|------|-----------------|
| Compile-time | KASAN, UBSAN, KCSAN | Memory bugs, UB, races |
| Compile-time | lockdep | Deadlock potential |
| Compile-time | sparse/smatch/coccinelle | Type errors, API misuse |
| Runtime (dev) | kgdb | Step-through debugging |
| Runtime (dev) | ftrace | Function-level tracing |
| Runtime (prod) | perf | Performance profiling |
| Runtime (prod) | eBPF/bpftrace | Dynamic probing |
| Post-mortem | kdump + crash | Crash dump analysis |

The golden rule: **Use multiple layers**. KASAN + lockdep running together catch entirely different classes of bugs than either alone.

USER: Explain concurrency and synchronization in the kernel. Cover preemption models, RCU deep dive, memory barriers, lock-free data structures, per-CPU variables, atomic operations, and the Linux kernel memory model (LKMM).
BOT: ## Concurrency & Synchronization — Kernel Level

### Preemption Models

Linux supports different preemption models (configured at build time):

**CONFIG_PREEMPT_NONE (Server):**
- No forced preemption of kernel code
- Kernel thread runs until it voluntarily yields (blocks, returns to user, calls `schedule()`)
- Lowest overhead, worst latency

**CONFIG_PREEMPT_VOLUNTARY (Desktop):**
- Explicit preemption points throughout kernel code (`might_sleep()`, `cond_resched()`)
- Balances throughput and latency
- Default for most distributions

**CONFIG_PREEMPT (Low-Latency Desktop/Embedded):**
- Kernel can be preempted anywhere except critical sections (spinlock-held, preempt_disable)
- Higher overhead but bounded latency
- RT applications

**CONFIG_PREEMPT_RT (Real-Time):**
- Converts nearly all spinlocks to `rt_mutex` (sleeping locks)
- Makes almost all kernel code preemptible
- Interrupt handlers run as kernel threads (threaded IRQs)
- Hard real-time guarantees

```c
// preempt_disable/preempt_enable — the fundamental preemption gate:
preempt_disable();   // Increments preempt_count — kernel won't be preempted
// ... critical work ...
preempt_enable();     // Decrements — if reaches 0 and reschedule pending, calls schedule()

// get_cpu() = preempt_disable() + smp_processor_id() — common pattern:
int cpu = get_cpu();  // Get current CPU AND disable preemption
// ... use per-CPU data for this cpu ...
put_cpu();            // Re-enable preemption
```

### RCU — Read-Copy-Update Deep Dive

RCU is the crown jewel of Linux synchronization. It solves the problem of read-heavy data structures where writers are rare.

**The problem RCU solves:**
```c
// Without RCU — reader must hold a lock (contention on hot path):
read_lock(&lock);
element = lookup(key);
use(element);
read_unlock(&lock);

// With RCU — reader pays zero synchronization overhead:
rcu_read_lock();                      // Just disable preemption (on non-PREEMPT_RT)
element = rcu_dereference(head_ptr);  // Compiler barrier + address dependency
use(element);                         // Safe to use — won't be freed until grace period
rcu_read_unlock();                    // Re-enable preemption
```

**RCU Grace Period:**
The guarantee: if a reader started before the grace period began, it will finish before the grace period ends.

```
Time →
Reader A: |--[read]--|           ← Started before GP, finishes during GP
Reader B:        |--[read]--|    ← Started during GP
Writer:   [grace period start]......[grace period end] → free old version
Synchronize:  call_rcu() calls callback AFTER GP ends

After GP ends, no reader has a reference to the old data → safe to free.
```

**How grace periods are detected:**
1. Classical RCU: Every CPU goes through a quiescent state (context switch, user mode execution, idle)
2. When ALL CPUs have passed through a quiescent state → grace period complete
3. `synchronize_rcu()` blocks until GP complete; `call_rcu(callback)` schedules callback for after GP

**RCU Variants in Linux:**
```
RCU             — wait for readers (rcu_read_lock/unlock)
SRCU            — sleepable RCU (readers can sleep)
Tasks RCU       — wait for voluntary context switches
Tasks Trace RCU — wait for trampolines (BPF, ftrace)
```

**Real RCU usage — deleting from a linked list:**
```c
// Writer: delete element "B" from A→B→C list
spin_lock(&list_lock);
struct element *old = list->b;
list->a->next = list->b->next;   // A→C
spin_unlock(&list_lock);
// At this point: any existing readers still see B (it's not freed yet)
// New readers will see A→C
synchronize_rcu();                // Wait for all existing readers
kfree(old);                       // Now safe — no reader holds a reference to B
```

### Memory Barriers

CPUs and compilers reorder memory operations for performance. Barriers prevent this:

```c
// Hardware memory ordering models (strongest → weakest):
// x86: TSO (Total Store Order) — very strong. Only Store-Load reordering.
// ARM: Weakly ordered — almost anything can be reordered.
// RISC-V: Weakly ordered (RVWMO — RISC-V Weak Memory Ordering).
// PowerPC: Infamous for aggressive reordering.

// Barrier types:
smp_mb();        // Full memory barrier — nothing crosses this point
smp_rmb();       // Read barrier — no reads before barrier reordered after
smp_wmb();       // Write barrier — no writes before barrier reordered after
smp_read_barrier_depends(); // Obsolete (address dependencies respected on all architectures now)

// Example: message passing pattern
// Thread A (producer):
data = 42;
smp_wmb();       // Ensure 'data' write is visible before 'flag' write
flag = 1;

// Thread B (consumer):
if (flag) {
    smp_rmb();   // Ensure 'flag' read is visible before 'data' read
    use(data);   // Guaranteed to see data = 42
}
// On x86: smp_wmb/smp_rmb are compiler barriers only (no hardware instruction)
// On ARM: smp_wmb → dmb st (Data Memory Barrier — stores)
```

### Atomic Operations

```c
// Architecture-independent (linux/atomic.h):
atomic_t counter = ATOMIC_INIT(0);

atomic_inc(&counter);          // atomic counter++
atomic_dec(&counter);          // atomic counter--
atomic_add(5, &counter);       // atomic counter += 5
int old = atomic_add_return(3, &counter);  // atomically add and return old value
int val = atomic_read(&counter);   // READ_ONCE() — single copy atomic read

// Atomic bit operations:
set_bit(NR, &flags);           // Atomically set bit
clear_bit(NR, &flags);         // Atomically clear bit
test_and_set_bit(NR, &flags);  // Atomically test and set, return old value
test_and_clear_bit(NR, &flags);
change_bit(NR, &flags);        // Atomically flip bit

// Atomic compare-and-swap (CAS) — the universal primitive:
int old_val = READ_ONCE(*ptr);
int new_val;
do {
    new_val = compute(old_val);
    // cmpxchg: if *ptr == old_val, set *ptr = new_val, return old_val
    // If someone changed *ptr between read and cmpxchg, old_val ≠ *ptr, retry
} while (!atomic_try_cmpxchg(ptr, &old_val, new_val));

// Under the hood on x86:
// lock cmpxchg [ptr], new_val   ← LOCK prefix makes it atomic across all CPUs
```

### Per-CPU Variables

Eliminates cache line bouncing by giving each CPU its own copy:

```c
// Define a per-CPU variable:
DEFINE_PER_CPU(int, my_counter);

// Access current CPU's copy (must be in preempt-safe context):
int cpu_val = this_cpu_read(my_counter);
this_cpu_inc(my_counter);

// Access any CPU's copy:
int cpu3_val = per_cpu(my_counter, 3);

// Common use case: statistics counters (no lock needed!):
this_cpu_inc(irq_count);  // Increment current CPU's IRQ counter — atomic for this CPU

// Total across all CPUs:
int total = 0;
for_each_possible_cpu(cpu)
    total += per_cpu(my_counter, cpu);
```

### Lock-Free Data Structures

**Lock-free ring buffer (kfifo):**
```c
// Writer advances 'in' index, reader advances 'out' index
// They never write to the same cache line (false sharing avoided)
struct kfifo {
    unsigned int in;     // Writer's index
    unsigned int out;    // Reader's index
    unsigned int mask;   // size - 1 (power of 2)
    void *data;
};

int kfifo_put(struct kfifo *fifo, const void *val) {
    // Writer (only one at a time via external locking):
    unsigned int next = READ_ONCE(fifo->in) + 1;
    if (next - READ_ONCE(fifo->out) > fifo->mask)  // Full?
        return -ENOSPC;
    memcpy(fifo->data + (fifo->in & fifo->mask), val, size);
    smp_wmb();  // Make data visible before index update
    WRITE_ONCE(fifo->in, next);  // Publish — reader can now see this entry
    return 0;
}
```

### Linux Kernel Memory Model (LKMM)

LKMM is a formal model of what memory ordering guarantees the Linux kernel provides. It's defined in the `tools/memory-model/` directory and verified with the `herd7` simulator.

Key macros and their semantics:
```c
// READ_ONCE / WRITE_ONCE — single-copy atomic access:
// Prevents compiler from splitting, merging, or inventing accesses
int val = READ_ONCE(*ptr);         // Atomic read (as a single instruction)
WRITE_ONCE(*ptr, val);             // Atomic write

// Address dependency ordering (guaranteed on all architectures):
int *ptr = READ_ONCE(global_ptr);  // Read pointer
int val = READ_ONCE(*ptr);         // Read through pointer — ordered after ptr read!
// This works because CPUs preserve address dependencies!
// (Alpha is the ONLY exception — it needs an mb. Nobody runs Linux on Alpha anymore.)

// Control dependency ordering:
if (READ_ONCE(a))
    WRITE_ONCE(b, 1);
// The write to 'b' is ordered after the read of 'a' on most architectures
// This is an implicit barrier caused by conditional execution
```

LKMM rules in practice:
1. **Two WRITE_ONCE to different locations**: NOT ordered without a barrier
2. **WRITE_ONCE then READ_ONCE**: NOT ordered on Alpha (but IS ordered on x86/ARM/RISC-V)
3. **READ_ONCE through a pointer**: Ordered (address dependency)
4. **Same-location access**: Always ordered (coherence — all CPUs see writes to the same location in the same order)

USER: Explain cross-architecture OS development. Cover the differences between x86, x86_64, ARM (AArch32/AArch64), and RISC-V (RV32/RV64), how to write portable kernel code, endianness handling, memory model differences, and the abstractions Linux uses to support 30+ architectures.
BOT: ## Cross-Architecture OS Development

### Architecture Families

| Feature | x86_64 | ARM64 (AArch64) | RISC-V64 |
|---------|--------|-----------------|----------|
| **Word size** | 64-bit | 64-bit | 64-bit |
| **Endianness** | Little | Little (or big) | Little (or big) |
| **Page sizes** | 4KB, 2MB, 1GB | 4KB, 16KB, 64KB | 4KB, 2MB, 1GB |
| **Virtual addr bits** | 48 (or 57) | 39 or 48 | 39 (Sv39) or 48 (Sv48) |
| **Privilege levels** | Ring 0-3 | EL0-3 | U/S/M modes |
| **Syscall instruction** | syscall | svc #0 | ecall |
| **TLB flush** | invlpg | tlbi vmalle1is | sfence.vma |
| **Fence/barrier** | mfence/lfence/sfence | dmb/dsb/isb | fence iorw, iorw |
| **I/O model** | Port I/O + MMIO | MMIO only | MMIO only |
| **Interrupt controller** | APIC/x2APIC | GICv2/v3 | PLIC + CLINT |
| **Timer** | PIT/HPET/TSC | ARM Generic Timer | mtime/mtimecmp |
| **Cache coherence** | Hardware (MESI) | Hardware | Hardware |
| **Memory model** | TSO (strong) | Weak | Weak (RVWMO) |
| **FPU/SIMD** | x87/SSE/AVX | NEON/SVE | F/D/V extensions |

### Port I/O vs MMIO — The x86 Oddity

x86 has a separate I/O address space — the ONLY widely-used architecture that does:

```c
// x86 port I/O:
outb(0x60, 0xF4);  // Write to I/O port 0x60
uint8_t val = inb(0x60);  // Read from I/O port 0x60

// All other architectures: use MMIO
void __iomem *regs = ioremap(phys_addr, 0x1000);
writel(val, regs + REG_OFFSET);
val = readl(regs + REG_OFFSET);
```

Linux abstracts this: `inb`/`outb` exist on all architectures but are only meaningful on x86. On ARM/RISC-V, they would just be empty or map to MMIO for compatibility with legacy drivers.

### Endianness Handling

```c
// Always use these macros, never assume byte order:
#include <asm/byteorder.h>

u16 val16 = le16_to_cpu(le_val);   // Little-endian to CPU byte order
u32 val32 = be32_to_cpu(be_val);   // Big-endian to CPU byte order
cpu_to_le32(val);                   // CPU to little-endian
cpu_to_be16(val);                   // CPU to big-endian

// On little-endian systems (x86, ARM, RISC-V default):
// le16_to_cpu() → no-op
// be16_to_cpu() → byteswap

// On big-endian systems (some ARM, POWER):
// le16_to_cpu() → byteswap
// be16_to_cpu() → no-op
```

This matters for: network protocols (big-endian!), filesystem on-disk structures (can be either), PCI config space (little-endian), device registers (varies).

### Memory Model Differences

```c
// x86 (TSO): Strong ordering
// - Loads are not reordered with loads
// - Stores are not reordered with stores
// - Stores are not reordered with prior loads
// - Only: Loads may be reordered with prior stores (store buffer)

// ARM/RISC-V: Weak ordering
// - ANYTHING can be reordered unless explicitly prevented

// This means:
// Code that works fine on x86 may have subtle bugs on ARM!

// Two threads, no synchronization:
// Thread A:                Thread B:
// data = 42;               while (!flag) {}
// flag = 1;                use(data);

// On x86: Works. Stores are ordered. Thread B always sees data=42.
// On ARM: Broken! Thread B may see flag=1 but data=0 (stores reordered).
// Fix: smp_wmb() between stores, smp_rmb() between loads.
```

### Linux Architecture Abstraction Layer

Linux supports 30+ architectures by pushing architecture-specific code into `arch/`:

```
arch/
├── x86/
│   ├── kernel/     # x86-specific kernel code
│   ├── mm/         # x86 page table code
│   ├── boot/       # x86 boot code
│   └── include/asm/ # x86 headers
├── arm64/
│   ├── kernel/
│   ├── mm/
│   └── include/asm/
├── riscv/
│   ├── kernel/
│   ├── mm/
│   └── include/asm/
└── ...
```

Each arch provides mandatory headers:
```c
// Every arch must define these (in arch/<name>/include/asm/):
#include <asm/types.h>       // Architecture-specific type sizes
#include <asm/page.h>        // PAGE_SIZE, PAGE_SHIFT
#include <asm/bitops.h>      // set_bit, clear_bit, ffz, fls
#include <asm/atomic.h>      // atomic operations
#include <asm/cmpxchg.h>     // compare-and-swap
#include <asm/barrier.h>     // mb, rmb, wmb, read_barrier_depends
#include <asm/io.h>          // readb/writel, inb/outb
#include <asm/tlbflush.h>    // flush_tlb_page, flush_tlb_range
#include <asm/pgtable.h>     // Page table entry format
#include <asm/ptrace.h>      // Register save/restore structure
#include <asm/processor.h>   // cpu_relax, thread_struct
#include <asm/cacheflush.h>  // Cache maintenance
```

### Writing Portable Kernel Code

```c
// DON'T — these are architecture-specific:
void __iomem *ptr;
u32 val = *(volatile u32 *)ptr;  // May not work on some ARMs (alignment, caching)
int size = sizeof(long);          // Different on 32-bit vs 64-bit!

// DO — use kernel abstractions:
u32 val = readl(ptr);             // Handles endianness, barriers, alignment
int size = sizeof(unsigned long); // Clear intent: this varies by word size

// DON'T — assume register names:
void get_sp(void) {
    u64 sp;
    __asm__("mov %%rsp, %0" : "=r"(sp));  // Only works on x86_64
}

// DO — use portable macros:
#include <asm/processor.h>
u64 sp = current_stack_pointer;   // Works everywhere

// DON'T — direct cache operations:
__asm__("wbinvd");  // x86-specific

// DO — use kernel API:
#include <asm/cacheflush.h>
flush_dcache_page(page);           // Portable cache maintenance

// DO — use sized types for on-disk/network structures:
struct disk_header {
    __le32 magic;     // Exactly 4 bytes, little-endian, regardless of CPU
    __be16 version;   // Exactly 2 bytes, big-endian
    __u64 size;       // Exactly 8 bytes
} __packed;

// DO — use page size abstractions:
#define MY_BUF_SIZE (4 * PAGE_SIZE)  // 16KB on most, 256KB with 64KB pages
// Not: #define MY_BUF_SIZE 16384    // Wrong on ARM64 with 64KB page granularity
```

### Start an Architecture Port — The Minimum

```c
// Minimum files needed for a new architecture port (arch/myarch/):

// 1. Kconfig — architecture selection
config MYARCH
    def_bool y
    select DMA_DIRECT_REMAP
    select GENERIC_IRQ_SHOW
    select HAVE_ARCH_KGDB
    # ...

// 2. Makefile
KBUILD_DEFCONFIG := defconfig
KBUILD_IMAGE := arch/myarch/boot/Image
head-y := arch/myarch/kernel/head.o

// 3. include/asm/types.h — sizes
typedef unsigned short umode_t;

// 4. include/asm/page.h
#define PAGE_SHIFT  12
#define PAGE_SIZE   (_AC(1, UL) << PAGE_SHIFT)

// 5. include/asm/barrier.h
#define mb()    __asm__ __volatile__("fence iorw, iorw" ::: "memory")  // RISC-V
#define rmb()   __asm__ __volatile__("fence ir, ir" ::: "memory")
#define wmb()   __asm__ __volatile__("fence ow, ow" ::: "memory")

// 6. kernel/head.S — boot entry (assembly)
// 7. kernel/setup.c — early init (C)
// 8. kernel/entry.S — syscall/interrupt entry
// 9. mm/init.c — page table setup
// + timer, IRQ controller, serial driver...
```

### QEMU for Architecture Development

```bash
# Test on different architectures without hardware:
qemu-system-x86_64   -kernel bzImage -append "console=ttyS0" -nographic
qemu-system-aarch64  -M virt -cpu cortex-a57 -kernel Image -nographic
qemu-system-riscv64  -M virt -kernel Image -nographic
qemu-system-arm      -M versatilepb -kernel zImage -nographic
qemu-system-ppc64    -M pseries -kernel vmlinux
qemu-system-mips64el -M malta -kernel vmlinux

# GDB debugging:
qemu-system-aarch64 -M virt -cpu cortex-a57 -kernel Image -S -s
# GDB connects: target remote localhost:1234
```

### Common Porting Pitfalls
1. **Uninitialized memory reads**: x86 sets memory to zero at boot; some ARMs don't
2. **Unaligned access**: x86 handles it in hardware (with penalty). ARM/RISC-V may fault
3. **Cache coherency**: On ARM, you must flush caches after modifying page tables. x86 does it automatically.
4. **Timer frequency**: Don't assume CONFIG_HZ=250 — it varies by arch (100 on some embedded)
5. **FPU context**: Always use `kernel_fpu_begin()`/`kernel_fpu_end()` for kernel FPU use — x86 saves/restores, ARM may not
6. **Stack size**: 16KB on x86_64, but could be 8KB on 32-bit or configurable on embedded
