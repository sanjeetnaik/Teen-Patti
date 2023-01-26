import React, { createRef } from 'react';
import ReactLoading from "react-loading"

function StartScreen({getDetails, showLoading}) {

    let user_name = createRef();
    let stack = createRef();

    return (
        <div className='bg-[#202020]'>
        <div className="bg-mobile-splash sm:bg-splash h-screen text-slate-200 bg-contain bg-no-repeat bg-center" >
            { showLoading ? 
            <div className='absolute top-1/4 left-1/2 -translate-x-1/2' >
                <ReactLoading type="spin" color="#efefef" width={250} />
            </div> 
            : 
            <div className='w-full sm:w-5/12 md:w-4/12 lg:w-3/12 xl:w-3/12 rounded-lg absolute top-1/2 left-1/2 -translate-y-1/2 
            -translate-x-1/2 p-5 bg-black/80' >
                <div>
                    <h3 className="text-xl sm:text-lg lg:text-xl xl:text-2xl text-center font-['Mulish'] font-light tracking-widest pb-4" >NEW GAME</h3>
                </div>
                <hr className='bg-white opacity-20' />
                <div className='p-4 sm:p-1 md:p-2 xl:px-2 xl:py-4 text-sm text-gray-300 text-center' >
                    <p>
                        Play free private online poker with your friends. <br/>
                        No download and no registration needed.
                    </p>
                </div>
                <div>
                    <h4 className='text-lg sm:text-base lg:text-lg' >
                        Your Nickname
                    </h4>
                    <input ref={user_name} className='bg-black/60 border-2 h-16 sm:h-10 lg:h-12 xl:h-16 w-full my-2 rounded-lg text-xl sm:text-lg lg:text-xl p-4' placeholder='Your Nickname' />
                    <h4 className='text-lg sm:text-base lg:text-lg' >
                        Your Stack
                    </h4>
                    <input ref={stack} type="number" className='bg-black/60 border-2 h-16 sm:h-10 lg:h-12 xl:h-16 w-full my-2 rounded-lg text-xl sm:text-lg lg:text-xl p-4' placeholder='Your Stack' />
                    
                    <button className="bg-[#3EA66C] my-2 w-full h-16 sm:h-10 lg:h-12 xl:h-16 rounded-lg text-xl sm:text-lg lg:text-xl font-bold tracking-wide" 
                        onClick={(e) => {
                            getDetails(user_name.current.value, stack.current.value);
                        }}
                    >
                        CREATE GAME
                    </button>
                </div>
            </div>
            }
        </div> 
        </div>
    );
}

export default StartScreen;