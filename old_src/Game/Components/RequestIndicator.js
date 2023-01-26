import React from 'react';

const RequestIndicator = ({numRequestWaiting}) => {
    return (
            <div className="rounded-full w-6 h-6 bg-red-600 absolute translate-y-0 -translate-x-1 text-white text-center font-bold" >
                {numRequestWaiting}
            </div>
    );
};

export default RequestIndicator;