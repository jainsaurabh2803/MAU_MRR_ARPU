# MAU_MRR_ARPU

TO calculate MAU for any product their could be two approach to it:
  1. Day Level :- If the product purchase data is 15th Mar 2018 and is purchased for one month then the next pruchase date is 15th April 2018, in this case if the product price is of $100, then in March-18 MRR would be $50 and same for April-18
  2. Month Level :-  If the product purchase data is 15th Mar 2018 and is purchased for one month then the next pruchase date is 15th April 2018, in this case if the product price is of $100, then entire Revenue would be consider in first month itself that is MRR in March-18 would be $100 and in April-2018 it would be $0 from this one customer

Pros and Cons of both the above views: 
    Pros - In first senario we are considering the actual start date and end date and the MRR is calculate on day level and then summed up to entire month, and In second senario their is very less complication in consedering which month to consider.
    Cons -  In first senario we are actual consedring the same cusotmer for two months, that is March and April which is giving the wrong image of Actual MAU count, this become worse in the case of quarterly and yearly plans but in second case we have to do extra effort in manupulating data so to get the end month correct which could result in error 
    
In all our codes we would be consedering all the senarios of Renewal, Upgrades,downgrades, Reactivation,Churn, migrated out and migrated within same plan

Sample data for both the logic can be found in this repo
