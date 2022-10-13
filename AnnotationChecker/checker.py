from goody import type_as_str
import inspect

class Check_All_OK:
    """
    Check_All_OK class implements __check_annotation__ by checking whether each
      annotation passed to its constructor is OK; the first one that
      fails (by raising AssertionError) prints its problem, with a list of all
      annotations being tried at the end of the check_history.
    """
       
    def __init__(self,*args):
        self._annotations = args
        
    def __repr__(self):
        return 'Check_All_OK('+','.join([str(i) for i in self._annotations])+')'

    def __check_annotation__(self, check,param,value,check_history):
        for annot in self._annotations:
            check(param, annot, value, check_history+'Check_All_OK check: '+str(annot)+' while trying: '+str(self)+'\n')


class Check_Any_OK:
    """
    Check_Any_OK implements __check_annotation__ by checking whether at least
      one of the annotations passed to its constructor is OK; if all fail 
      (by raising AssertionError) this classes raises AssertionError and prints
      its failure, along with a list of all annotations tried followed by the
      check_history.
    """
    
    def __init__(self,*args):
        self._annotations = args
        
    def __repr__(self):
        return 'Check_Any_OK('+','.join([str(i) for i in self._annotations])+')'

    def __check_annotation__(self, check,param,value,check_history):
        failed = 0
        for annot in self._annotations: 
            try:
                check(param, annot, value, check_history)
            except AssertionError:
                failed += 1
        if failed == len(self._annotations):
            assert False, repr(param)+' failed annotation check(Check_Any_OK): value = '+repr(value)+\
                         '\n  tried '+str(self)+'\n'+check_history                 



class Check_Annotation:
    # We start by binding the class attribute to True meaning checking can occur
    #   (but only when the function's self._checking_on is also bound to True)
    checking_on  = True
  
    # For checking the decorated function, bind its self._checking_on as True
    def __init__(self, f):
        self._f = f
        self._checking_on = True

    # Check whether param's annot is correct for value, adding to check_history
    #    if recurs; defines many local function which use it parameters.  
    def check(self,param,annot,value,check_history=''):
        # Define local functions for checking, list/tuple, dict, set/frozenset,
        #   lambda/functions, and str (str for extra credit)
        # Many of these local functions called by check, call check on their
        #   elements (thus are indirectly recursive)

        # We start by comparing check's function annotation to its arguments
        def check_sequence(t):
            assert isinstance(value, t), f"'{param}' failed annotation check(wrong type): value = {repr(value)}\n  was type {type_as_str(value)} ...should be type {str(annot)[8:len(str(annot))-2]}\n{check_history}"
            if len(annot) < 2:
                for ind, val in enumerate(value):
                    self.check(param, annot[0], val, check_history+type_as_str(value)+'['+str(ind)+' ] check: '+str(annot[0])+'\n')
            else:
                assert not len(annot) != len(value), 'Incorrect number of elements'
                for ind, val in enumerate(value):
                    self.check(param, annot[ind], val, check_history+type_as_str(value)+'['+str(ind)+' ] check: '+str(annot[0])+'\n')
        def check_dict():
            assert isinstance(value, dict), f"'{param}' failed annotation check(wrong type): value = {repr(value)}\n  was type {type_as_str(value)} ...should be type {str(annot)[8:len(str(annot))-2]}\n{check_history}"
            if len(annot) > 1:
                assert 1 == 2, repr(param)+' annotation inconsistency: dict should have 1 value but had '+str(len(annot))+\
                              '\n  annotation = '+str(annot)+'\n'+check_history
            else:
                key_to_store, value_to_store = None, None
                for key, val in annot.items():
                    key_to_store, value_to_store = key, val
                for k, v in value.items():
                    self.check(param, key_to_store, k)
                    self.check(param, value_to_store, v)
                
        def check_set(t):
            assert isinstance(value, t), f"'{param}' failed annotation check(wrong type): value = {repr(value)}\n  was type {type_as_str(value)} ...should be type {str(annot)[8:len(str(annot))-2]}\n{check_history}"
            if len(annot) > 1:
                assert 1 == 2, repr(param)+' annotation inconsistency: '+str(t)+' should have 1 value but had '+str(len(annot))+\
                              '\n  annotation = '+str(annot)+'\n'+check_history
            else:
                local = None
                for a in annot:
                    local = a
                for val in value:
                    self.check(param, local, val, check_history+type_as_str(t)+' value check: '+str(local)+'\n')
        
        def check_predicate():
            assert len(inspect.getargspec(annot).args) == 1, f" annotation inconsistency: predicate should have 1 parameter but had {inspect.getargspec(annot).args}\n  predicate = {str(annot)}\n{check_history}"
            try:
                result = annot(value)
                e = None
            except Exception as j:
                e = AssertionError
                p = repr(param)+' annotation predicate('+str(annot)+') raised exception'+\
                              '\n  exception = '+type_as_str(j)+': '+str(j)+'\n'+check_history
            else:
                assert result == True, f"'{param}' failed annotation check: value = {repr(value)}\n  predicate = {str(annot)}\n{check_history}"
            finally:
                if e != None:
                    raise e(p)
                
        def check_str():
            try:
                result = eval(annot, dict(self._args))
                e = None
            except Exception as j:
                e = AssertionError
                p = repr(param)+' annotation predicate('+str(annot)+') raised exception'+\
                              '\n  exception = '+type_as_str(j)+': '+str(j)+'\n'+check_history
            else:
                assert result == True, f"'{param}' failed annotation check: value = {repr(value)}\n  predicate = {str(annot)}\n{check_history}"
            finally:
                if e != None:
                    raise e(p)
        if annot == None:
            pass
        elif type(annot) is type:
            if not isinstance(value, annot):
                raise AssertionError(f"'{param}' failed annotation check(wrong type): value = {repr(value)}\n  was type {type_as_str(value)} ...should be type {str(annot)[8:len(str(annot))-2]}\n{check_history}")
        elif type(annot) is list: check_sequence(list)
        elif type(annot) is tuple: check_sequence(tuple)
        elif type(annot) is dict: check_dict()
        elif type(annot) is set: check_set(set)
        elif type(annot) is frozenset: check_set(frozenset)
        elif inspect.isfunction(annot): check_predicate()
        elif type(annot) is str: check_str()
        else:
            try:
                annot.__check_annotation__(self.check,param,value,check_history)
            except Exception as m:
                raise AssertionError(f" annotation protocol({str(annot)}) raised exception\n  exception = {type_as_str(m)}: {m}\n{check_history}")
                
        
        
    # Return result of calling decorated function call, checking present
    #   parameter/return annotations if required
    def __call__(self, *args, **kargs):

        # Returns the parameter->argument bindings as an OrderedDict, derived
        #   from dict, binding the function header's parameters in order

        def param_arg_bindings():
            f_signature  = inspect.signature(self._f)
            bound_f_signature = f_signature.bind(*args,**kargs)
            for param in f_signature.parameters.values():
                if not (param.name in bound_f_signature.arguments):
                    bound_f_signature.arguments[param.name] = param.default
            return bound_f_signature.arguments

        # If annotation checking is turned off at the class or function level
        #   just return the result of calling the decorated function
        # Otherwise do all the annotation checking
        if not Check_Annotation.checking_on or not self.checking_on:
            return self._f(*args, **kargs)
        self._args = param_arg_bindings()
        try:
            # Check the annotation for each of the annotated parameters
            for arg in self._args:
                if arg in self._f.__annotations__:
                    self.check(arg, self._f.__annotations__[arg], self._args[arg])
            # Compute/remember the value of the decorated function
            ans = self._f(*args, **kargs)
            if 'return' in self._f.__annotations__:
                self._args['_return'] = ans
                self.check('return',self._f.__annotations__['return'],ans)
            return ans
            # If 'return' is in the annotation, check it
            
            # Return the decorated answer
            
            pass #remove after adding real code in try/except
            
        #On first AssertionError, print the source lines of the function and reraise 
        except AssertionError:
            # print(80*'-')
            # for l in inspect.getsourcelines(self._f)[0]: # ignore starting line #
            #     print(l.rstrip())
            # print(80*'-')
            raise




  
if __name__ == '__main__':     
    # an example of testing a simple annotation  
    def f(x:int): pass
    f = Check_Annotation(f)
    # f(3)
    # f('a')